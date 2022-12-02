# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import models, api, fields
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    picked_rate = fields.Float(
        compute='_compute_picked_rate',
        help='Rate of received products',
        store=True,
    )

    @api.depends('state', 'order_line.qty_received', 'order_line.product_qty')
    def _compute_picked_rate(self):
        precision = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure'
        )
        for purchase in self:
            received_count = 0
            line_count = 0
            purchase.picked_rate = 0
            for line in purchase.order_line:
                if line.product_type in (
                    'consu', 'product'
                ) and line.product_qty > 0:
                    line_count += 1
                    if float_compare(
                        line.qty_received,
                        line.product_qty,
                        precision_digits=precision
                    ) >= 0:
                        received_count += 1
            if line_count > 0:
                purchase.picked_rate = \
                    received_count * 100 / line_count

    def action_update_picked_rate(self):
        self._compute_picked_rate()
