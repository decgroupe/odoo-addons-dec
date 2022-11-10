# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2022

from odoo import models, api, fields
from odoo.tools import float_compare, float_is_zero


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_status = fields.Selection(
        [
            ('full', 'Fully Delivered'),
            ('todo', 'To Deliver'),
            ('none', 'Nothing to Deliver'),
        ],
        string='Delivery Status',
        compute='_compute_delivery_status',
        store=True,
        readonly=True
    )

    @api.multi
    @api.depends(
        'state', 'qty_delivered', 'product_uom_qty', 'display_type',
        'invoice_status'
    )
    def _compute_delivery_status(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        for rec in self.filtered(lambda x: not x.display_type):
            if float_is_zero(
                rec.product_uom_qty, precision
            ):
                rec.delivery_status = 'none'
            elif float_compare(
                rec.qty_delivered,
                rec.product_uom_qty,
                precision_digits=precision
            ) >= 0:
                rec.delivery_status = 'full'
            else:
                rec.delivery_status = 'todo'


# not display_type and qty_delivered &lt; product_uom_qty and invoice_status in ['no', 'to invoice'])