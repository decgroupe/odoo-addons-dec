# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import  fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_validate = fields.Boolean(
        'Auto Validate',
        old_name="openupgrade_legacy_8_0_auto_validate",
        help="Also validate linked moves when this move is validated.",
        copy=False,
    )

    def _action_done(self):
        res = super()._action_done()
        auto_validated_moves = res.\
            mapped('move_dest_ids').\
            filtered(lambda m: m.auto_validate and m.state == 'assigned')
        for move in auto_validated_moves:
            # Apply logic from addons/stock/wizard/stock_immediate_transfer.py
            # and process every move lines
            for move_line in move.move_line_ids:
                move_line.qty_done = move_line.product_uom_qty
        # Finally call action_done
        if auto_validated_moves:
            auto_validated_moves._action_done()
        return res
