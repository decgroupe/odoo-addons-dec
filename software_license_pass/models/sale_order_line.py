# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from datetime import datetime, timedelta, date
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_pass_values(self, pack_id):
        return {
            'origin': self.order_id.name,
            'sale_order_id': self.order_id.id,
            'sale_order_line_id': self.id,
            'user_id': self.order_id.user_id.id,
            'company_id': self.order_id.company_id.id,
            'product_id': self.product_id.id,
            'pack_id': pack_id.id,
        }

    def _create_application_pass(self):
        vals = self._prepare_pass_values(self.product_id.license_pack_id)
        pass_id = self.env['software.license.pass'].create(vals)
        pass_id.sync_with_pack()
        # Post-write pass data to propagate values to all licences
        today = fields.Date.from_string(fields.Date.context_today(self))
        pass_id.write(
            {
                'partner_id': self.order_id.partner_shipping_id.id,
                'max_allowed_hardware': self.product_uom_qty,
                'expiration_date': today + timedelta(days=365),
            }
        )

    def _timesheet_service_generation(self):
        """Handle task creation with sales order's project."""
        line_ids = self.filtered(
            lambda sol: (
                sol.is_service and sol.product_id.service_tracking ==
                'create_application_pass'
            )
        )
        for line_id in line_ids:
            line_id._create_application_pass()
        return super()._timesheet_service_generation()

    @api.multi
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        line_ids = self.filtered(
            lambda sol: sol.is_service and sol.product_id.service_tracking ==
            'create_application_pass'
        )
        for line_id in line_ids:
            line_id.qty_delivered = line_id.product_uom_qty
