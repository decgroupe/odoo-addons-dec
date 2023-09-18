# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import _, api, fields, models


class SoftwareLicensePass(models.Model):
    _name = "software.license.pass"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Application Pass"
    _order = "name desc"

    @api.model
    def _get_default_serial(self):
        return self.env["software.license"]._generate_serial()

    @api.model
    def _get_current_user(self):
        return self.env.user

    @api.model
    def _get_default_company(self):
        return self.env.user.company_id

    active = fields.Boolean(
        string="Active",
        default=True,
        help="If unchecked, it will allow you to hide the application pass "
        "without removing it.",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        help="Product at the origin of the pass",
        change_default=True,
        domain="[('license_pack_id', '!=', False)]",
        ondelete="restrict",
    )
    pack_id = fields.Many2one(
        comodel_name="software.license.pack",
        string="Pack",
        help="Pack of applications linked to the product at the origin of " "the pass",
        change_default=True,
        ondelete="restrict",
    )
    name = fields.Char(
        string="Reference",
        copy=False,
        readonly=True,
        default=lambda x: _("New"),
    )
    state = fields.Selection(
        selection=[
            ("draft", "To Send"),
            ("sent", "Sent"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        index=True,
        tracking=True,
        default="draft",
    )
    serial = fields.Char(
        required=True,
        copy=False,
        default=_get_default_serial,
        tracking=True,
        help="Unique serial used as an authorization identifier",
    )
    expiration_date = fields.Datetime(
        string="Expiration Date",
        tracking=True,
        help="If set, then after this date it will not be possible to "
        "proceed or renew any activation.",
    )
    max_allowed_hardware = fields.Integer(
        string="Maximum Activation Count",
        default=1,
        tracking=True,
        help="If more than 0, then the number of registered hardware "
        "identifiers will not be allowed to be greater than this value.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=_get_default_company,
        copy=False,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        domain="[('share', '=', False)]",
        required=False,
        default=_get_current_user,
        tracking=True,
        copy=False,
    )
    origin = fields.Char(
        string="Source",
        copy=False,
        help="Reference of the document that generated this pass.",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        copy=False,
    )
    partner_referral_id = fields.Many2one(
        comodel_name="res.partner",
        string="Referral partner",
        copy=False,
        default=lambda self: self.partner_id,
        track_visibility="onchange",
    )
    license_ids = fields.One2many(
        comodel_name="software.license",
        inverse_name="pass_id",
        string="Licenses",
        copy=False,
        help="Licenses dynamically generated by this pass to match pack " "content",
    )

    _sql_constraints = [
        (
            "serial_uniq",
            "unique(serial)",
            "Serial Pass Activation Code must be unique!",
        ),
    ]

    @api.model
    def create(self, values):
        if not values.get("name", False) or values["name"] == _("New"):
            values["name"] = self.env["ir.sequence"].next_by_code(
                "software.license.pass"
            ) or _("New")
        app_pass = super(SoftwareLicensePass, self).create(values)
        return app_pass

    def write(self, vals):
        self._batch_license_write(vals)
        return super().write(vals)

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        if not default.get("serial"):
            default.update(serial=_("%s (copy)") % (self.serial))
        return super(SoftwareLicensePass, self).copy(default)

    def _batch_license_write(self, vals):
        licenses_vals = {}
        if "active" in vals:
            licenses_vals["active"] = vals.get("active")
        if "partner_id" in vals:
            licenses_vals["partner_id"] = vals.get("partner_id")
        if "max_allowed_hardware" in vals:
            licenses_vals["max_allowed_hardware"] = vals.get("max_allowed_hardware")
        if "expiration_date" in vals:
            licenses_vals["expiration_date"] = vals.get("expiration_date")
        if licenses_vals:
            license_ids = (
                self.with_context(active_test=False)
                .mapped("license_ids")
                .with_context(override_from_pass=True)
            )
            license_ids.write(licenses_vals)

    def _get_unique_hardware_names(self):
        self.ensure_one()
        return set(self.license_ids.mapped("hardware_ids").mapped("name"))

    def check_max_activation_reached(self, hardware_name):
        self.ensure_one()
        res = False
        if self.max_allowed_hardware > 0:
            hardware_names = self._get_unique_hardware_names()
            if hardware_name not in hardware_names:
                # If an hardware is already in our pass list, that means that
                # we don't care about max activation. Otherwise check for
                # already used slots count
                if len(hardware_names) >= self.max_allowed_hardware:
                    # We have already reached the maximum hardwares, we cannot
                    # accept new ones anymore.
                    res = True
        return res

    def get_remaining_activation(self):
        self.ensure_one()
        if self.max_allowed_hardware <= 0:
            return -1
        else:
            hardware_names = self._get_unique_hardware_names()
            return self.max_allowed_hardware - len(hardware_names)

    @api.model
    def action_view_base(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "software_license_pass.act_window_software_license_pass"
        )
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("software_license_pass.software_license_pass_form_view")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.id
        return action

    def action_cancel(self):
        self.write({"state": "cancel"})

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_as_sent"):
            self.filtered(lambda o: o.state == "draft").with_context(
                tracking_disable=True
            ).write({"state": "sent"})
            partner_ids = kwargs.get("partner_ids", False)
            if partner_ids:
                partner_ids = self.env["res.partner"].browse(partner_ids)
            else:
                partner_ids = self.mapped("partner_id")
            partner_ids.give_portal_access()
        return super(
            SoftwareLicensePass, self.with_context(mail_post_autofollow=True)
        ).message_post(**kwargs)

    def action_send(self):
        """This function opens a window to compose an email, with the pass
        template message loaded by default
        """
        self.ensure_one()
        self.user_id = self._get_current_user()
        self.partner_id.sudo().delegate_signup_prepare()
        template_id = self.env.ref("software_license_pass.email_template", False)
        form_id = self.env.ref("mail.email_compose_message_wizard_form", False)
        ctx = {
            "default_model": "software.license.pass",
            "default_res_id": self.id,
            "default_use_template": bool(template_id.id),
            "default_template_id": template_id.id,
            "default_composition_mode": "comment",
            "mark_as_sent": True,
            "model_description": _("Application Pass"),
            "custom_layout": "mail.mail_notification_light",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(form_id.id, "form")],
            "view_id": form_id.id,
            "target": "new",
            "context": ctx,
        }

    def _prepare_license_vals(self, pack_line_id):
        self.ensure_one()
        return {
            "type": "standard",
            "application_id": pack_line_id.application_id.id,
            "pass_id": self.id,
            "partner_id": self.partner_id.id,
            "pack_line_id": pack_line_id.id,
            "product_id": self.product_id.id,
            "expiration_date": self.expiration_date,
            "max_allowed_hardware": self.max_allowed_hardware,
            "feature_ids": False,
        }

    def action_resync_with_pack(self):
        for rec in self:
            for line in rec.pack_id.line_ids:
                if line not in rec.license_ids.mapped("pack_line_id"):
                    vals = rec._prepare_license_vals(line)
                    self.env["software.license"].with_context(
                        force_generate_serial=True
                    ).create(vals)
        self.mapped("license_ids").action_sync_features_with_template()
