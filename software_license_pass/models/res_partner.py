# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    pass_ids = fields.One2many(
        comodel_name="software.license.pass",
        compute="_compute_pass",
        string="Passes",
    )
    pass_count = fields.Integer(
        compute="_compute_pass",
        string="Number of Passes",
    )

    @api.depends("pass_ids", "is_company", "parent_id.is_company")
    def _compute_pass(self):
        for rec in self:
            domain = rec._get_pass_default_domain()
            rec.pass_ids = self.env["software.license.pass"].search(domain)
            rec.pass_count = len(rec.pass_ids)

    def action_view_pass(self):
        return self.with_context(active_test=False).pass_ids.action_view()

    def _get_pass_default_domain(self):
        self.ensure_one()
        partner_id = self
        while partner_id and not partner_id.is_company:
            partner_id = partner_id.parent_id
        if not partner_id:
            partner_id = self
        # with an `on_change` event, we need to get database ID from origin
        if isinstance(partner_id.id, models.NewId) and partner_id._origin:
            pid = partner_id._origin.id
        else:
            pid = partner_id.id
        res = [("partner_id", "child_of", pid)]
        if self.env.context.get("pass_sent_only"):
            res.append(("state", "=", "sent"))
        return res

    def _compute_license(self):
        # self_nopass = self.with_context(include_pass_licenses=False)
        return super(ResPartner, self)._compute_license()

    def _get_license_default_domain(self):
        res = super()._get_license_default_domain()
        # include licenses from passes
        if self.env.context.get("include_pass_licenses"):
            if self.env.context.get("pass_sent_only"):
                res += [
                    ("|"),
                    ("pass_state", "=", "sent"),
                    ("pass_id", "=", False),
                ]
            else:
                # without filter, we get all licenses
                pass
        else:
            # exclude licenses from passes
            res.append(("pass_id", "=", False))
        return res

