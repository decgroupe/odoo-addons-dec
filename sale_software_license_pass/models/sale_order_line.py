# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from datetime import datetime, timedelta, date
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    license_pass_ids = fields.One2many(
        comodel_name='software.license.pass',
        inverse_name='sale_order_line_id',
        string="Passes",
    )

    @api.multi
    def write(self, vals):
        result = super(SaleOrderLine, self).write(vals)
        # Changing the ordered quantity should change the maximum allowed of
        # hardware, whatever the SO state. It will be blocked by the super in
        # case of a locked sale order.
        if 'product_uom_qty' in vals:
            for line in self.filtered('license_pass_ids'):
                line.license_pass_ids.write(
                    {'max_allowed_hardware': vals.get('product_uom_qty')}
                )
        return result

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
        self.ensure_one()
        vals = self._prepare_pass_values(self.product_id.license_pack_id)
        pass_id = self.env['software.license.pass'].with_context(
            tracking_disable=True
        ).create(vals)
        pass_id.action_resync_with_pack()
        # Post-write pass data to propagate values to all licenses created
        # during the `action_resync_with_pack`
        today = fields.Date.from_string(fields.Date.context_today(self))
        vals = {
            'partner_id': self.order_id.partner_shipping_id.id,
        }
        if self.product_uom.category_id == self.env.ref(
            'software_license_pass.product_uom_categ_seatyear'
        ):
            qty = self.product_uom_qty
            years = self.product_uom.factor_inv
        elif self.product_uom.category_id == self.env.ref(
            'software_license_pass.product_uom_categ_yearseat'
        ):
            qty = self.product_uom.factor_inv
            years = self.product_uom_qty
        else:
            qty = 0
            years = False
        if qty:
            vals['max_allowed_hardware'] = qty
        if years:
            vals['expiration_date'] = today + timedelta(days=365 * years)
        pass_id.write(vals)
        return pass_id

    def _timesheet_service_generation(self):
        """Handle pass creation."""
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
    @api.depends(
        'license_pass_ids.state', 'license_pass_ids.max_allowed_hardware'
    )
    def _compute_qty_delivered(self):
        super(SaleOrderLine, self)._compute_qty_delivered()

        line_ids = self.filtered(
            lambda sol: sol.is_service and sol.product_id.service_tracking ==
            'create_application_pass'
        )
        for line_id in line_ids:
            pass_ids = line_id.license_pass_ids.filtered(
                lambda x: x.state == 'sent'
            )
            line_id.qty_delivered = sum(
                pass_id.max_allowed_hardware for pass_id in pass_ids
            )
