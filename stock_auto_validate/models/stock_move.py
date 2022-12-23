# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models
from odoo.tools.float_utils import float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    auto_validate = fields.Boolean(
        'Auto Validate',
        old_name="openupgrade_legacy_8_0_auto_validate",
        help="Also validate linked moves when this move is validated.",
        copy=False,
    )

    def _action_done(self, cancel_backorder=False):
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in res:
            move._action_auto_validate()
        return res

    def _action_auto_validate(self):
        self.ensure_one()
        auto_validated_moves = self.\
            mapped('move_dest_ids').\
            filtered(lambda m: m.auto_validate and m.state == 'assigned')
        # If initial quantity changed to 0, then do not auto_validate
        # descendants moves
        if float_is_zero(
            self.product_uom_qty,
            precision_rounding=self.product_id.uom_id.rounding
        ):
            auto_validated_moves._do_unreserve()
        else:
            for move in auto_validated_moves:
                # Apply logic from addons/stock/wizard/stock_immediate_transfer.py
                # and process every move lines
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            # Finally call action_done
            if auto_validated_moves:
                auto_validated_moves._action_done()
