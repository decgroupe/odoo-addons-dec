# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_delivered_method = fields.Selection(
        selection_add=[("application_pass", "Application Pass")],
    )
    is_application_pass = fields.Boolean(
        string="Is an Application Pass",
        compute="_compute_is_application_pass",
        store=True,
        compute_sudo=True,
        help="Sales Order item should generate an application pass from the pack "
        "define on the product settings.",
    )
    license_pass_ids = fields.One2many(
        comodel_name="software.license.pass",
        inverse_name="sale_order_line_id",
        string="Passes",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if line.state == "sale" and line.qty_delivered_method == "application_pass":
                line.sudo()._application_pass_generation()
                # if the SO line creates a pass when the sale has already been
                # confirmed, post a message on the order
                if len(line.license_pass_ids) == 1:
                    record_link = "<a href=# data-oe-model=%s data-oe-id=%d>%s</a>" % (  # noqa: UP031
                        line.license_pass_ids._name,
                        line.license_pass_ids.id,
                        line.license_pass_ids.name,
                    )
                    msg_body = _(
                        "Pass Created (%(product_name)s): %(link)s",
                        product_name=line.product_id.name,
                        link=record_link,
                    )
                    line.order_id.message_post(body=msg_body)
        return lines

    def write(self, vals):
        result = super().write(vals)
        # Changing the ordered quantity should change the maximum allowed of
        # hardware, whatever the SO state. It will be blocked by the super in
        # case of a locked sale order.
        if "product_uom_qty" in vals:
            for line_id in self:
                if line_id.license_pass_ids:
                    sale_pass_data = line_id._get_sale_application_pass_data(
                        line_id.order_id.date_order
                    )
                    # We keep only the expiration date because line UoM is not
                    # editable after order confirmation and because the partner
                    # could be changed manually directly in the application
                    # pass
                    line_id.license_pass_ids.write(
                        {"expiration_date": sale_pass_data.get("expiration_date")}
                    )
        return result

    def _get_sale_application_pass_data(self, start_date):
        self.ensure_one()
        res = {}
        if self.product_uom.category_id == self.env.ref(
            "software_license_pass.product_uom_categ_seatyear"
        ):
            qty = self.product_uom_qty
            years = self.product_uom.factor_inv
        elif self.product_uom.category_id == self.env.ref(
            "software_license_pass.product_uom_categ_yearseat"
        ):
            qty = self.product_uom.factor_inv
            years = self.product_uom_qty
        else:
            qty = 0
            years = False
        if qty:
            res["max_allowed_hardware"] = qty
        if years:
            res["expiration_date"] = start_date + timedelta(days=365 * years)
        return res

    def _prepare_pass_values(self, pack_id):
        return {
            "origin": self.order_id.name,
            "sale_order_id": self.order_id.id,
            "sale_order_line_id": self.id,
            "user_id": self.order_id.user_id.id,
            "company_id": self.order_id.company_id.id,
            "product_id": self.product_id.id,
            "pack_id": pack_id.id,
        }

    def _create_application_pass(self):
        self.ensure_one()
        # Check if quantity is positive before creating a new pass
        if (
            float_compare(
                self.product_uom_qty, 0.0, precision_rounding=self.product_uom.rounding
            )
            <= 0
        ):
            return False
        vals = self._prepare_pass_values(self.product_id.license_pack_id)
        pass_id = (
            self.env["software.license.pass"]
            .with_context(tracking_disable=True)
            .create(vals)
        )
        pass_id.action_resync_with_pack()
        # Post-write pass data to propagate values to all licenses created
        # during the `action_resync_with_pack`
        today = fields.Date.from_string(fields.Date.context_today(self))
        partner_shipping_id = self.order_id.partner_shipping_id
        vals = {
            "partner_id": partner_shipping_id.unfenced_commercial_partner_id.id,
            "partner_referral_id": partner_shipping_id.id,
        }
        sale_pass_data = self._get_sale_application_pass_data(today)
        vals.update(sale_pass_data)
        pass_id.write(vals)
        # create a to-send activity
        pass_id._create_to_send_activity(self, user_id=self.order_id.user_id.id)
        return pass_id

    def _application_pass_generation(self):
        """Handle pass creation."""
        line_ids = self.filtered(lambda sol: sol.is_application_pass)
        for line_id in line_ids:
            license_pass_ids = line_id.license_pass_ids.filtered(
                lambda lp: (lp.state != "cancel")
            )
            if not license_pass_ids or self.env.context.get(
                "force_create_application_pass"
            ):
                line_id._create_application_pass()
            else:
                _logger.warning(
                    "Pass already exists for this line: %s",
                    license_pass_ids.mapped("display_name"),
                )

    @api.depends("product_id")
    def _compute_qty_delivered_method(self):
        """Automatically select dedicated method to compute delivered quantities."""
        res = super()._compute_qty_delivered_method()
        line_ids = self.filtered(lambda sol: sol.is_application_pass)
        for line in line_ids:
            line.qty_delivered_method = "application_pass"
        return res

    @api.depends("license_pass_ids.state", "license_pass_ids.max_allowed_hardware")
    def _compute_qty_delivered(self):
        res = super()._compute_qty_delivered()
        line_ids = self.filtered(lambda sol: sol.is_application_pass)
        for line_id in line_ids:
            pass_ids = line_id.license_pass_ids.filtered(lambda x: x.state == "sent")
            if line_id.product_uom.category_id == line_id.env.ref(
                "software_license_pass.product_uom_categ_seatyear"
            ):
                line_id.qty_delivered = sum(
                    pass_id.max_allowed_hardware for pass_id in pass_ids
                )
            elif line_id.product_uom.category_id == self.env.ref(
                "software_license_pass.product_uom_categ_yearseat"
            ):
                if pass_ids.ids:
                    line_id.qty_delivered = line_id.product_uom_qty
                else:
                    line_id.qty_delivered = 0
        return res

    @api.depends("product_id.service_tracking")
    def _compute_is_application_pass(self):
        for so_line in self:
            so_line.is_application_pass = (
                so_line.is_service
                and so_line.product_id.service_tracking == "create_application_pass"
            )
