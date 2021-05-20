# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    received = fields.Boolean(
        string='Received',
        compute='_compute_received',
        help="If received, then the product should be available "
        "to be used on production",
    )

    @api.multi
    @api.depends(
        'state', 'reserved_availability', 'product_uom_qty', 'procure_method',
        'move_orig_ids'
    )
    def _compute_received(self):
        for move in self:
            move.received = False
            if move.state == 'done':
                move.received = True
            elif move.procure_method == 'make_to_order':
                if move.move_orig_ids and all(
                    m.state in ['cancel', 'done'] for m in move.move_orig_ids
                ):
                    move.received = True
            elif move.procure_method == 'make_to_stock':
                reserved = (move.reserved_availability == move.product_uom_qty)
                move.received = reserved
