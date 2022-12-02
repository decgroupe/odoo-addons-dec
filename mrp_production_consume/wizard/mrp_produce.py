# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from datetime import datetime

from odoo import _, api, fields, models
from odoo.tools import float_compare, float_round
from odoo.exceptions import UserError


class MrpProduce(models.TransientModel):
    _inherit = "mrp.product.produce"

    def do_produce(self):
        moves_to_finish = self.production_id.move_finished_ids.filtered(
            lambda x: x.state not in ('done', 'cancel')
        )
        if any([m.product_uom_qty == 0 for m in moves_to_finish]):
            raise UserError(
                _(
                    'You cannot produce a zero quantity, check finished products stock move quantities!'
                )
            )
        res = super().do_produce()
        return res

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        lines = []
        qty_todo = self.product_uom_id._compute_quantity(
            self.product_qty, self.production_id.product_uom_id, round=False
        )
        # Do not filter out moves not linked to a bom_line_id like it is done in
        # addons/mrp/wizard/mrp_product_produce.py
        for move in self.production_id.move_raw_ids.filtered(
            lambda m: m.state not in ('done', 'cancel')
        ):
            qty_to_consume = float_round(
                qty_todo * move.unit_factor,
                precision_rounding=move.product_uom.rounding
            )
            for move_line in move.move_line_ids:
                if float_compare(
                    qty_to_consume,
                    0.0,
                    precision_rounding=move.product_uom.rounding
                ) <= 0:
                    break
                if move_line.lot_produced_id or float_compare(
                    move_line.product_uom_qty,
                    move_line.qty_done,
                    precision_rounding=move.product_uom.rounding
                ) <= 0:
                    continue
                to_consume_in_line = min(
                    qty_to_consume, move_line.product_uom_qty
                )
                lines.append(
                    {
                        'move_id':
                            move.id,
                        'qty_to_consume':
                            to_consume_in_line,
                        'qty_done':
                            to_consume_in_line,
                        'lot_id':
                            move_line.lot_id.id,
                        'product_uom_id':
                            move.product_uom.id,
                        'product_id':
                            move.product_id.id,
                        'qty_reserved':
                            min(to_consume_in_line, move_line.product_uom_qty),
                    }
                )
                qty_to_consume -= to_consume_in_line
            if float_compare(
                qty_to_consume,
                0.0,
                precision_rounding=move.product_uom.rounding
            ) > 0:
                if move.product_id.tracking == 'serial':
                    while float_compare(
                        qty_to_consume,
                        0.0,
                        precision_rounding=move.product_uom.rounding
                    ) > 0:
                        lines.append(
                            {
                                'move_id': move.id,
                                'qty_to_consume': 1,
                                'qty_done': 1,
                                'product_uom_id': move.product_uom.id,
                                'product_id': move.product_id.id,
                            }
                        )
                        qty_to_consume -= 1
                else:
                    lines.append(
                        {
                            'move_id': move.id,
                            'qty_to_consume': qty_to_consume,
                            'qty_done': qty_to_consume,
                            'product_uom_id': move.product_uom.id,
                            'product_id': move.product_id.id,
                        }
                    )

        # In case of no lines were added, it could be because the production
        # order is done but some moves have been added after
        if qty_todo == 0 and not lines:
            for move in self.production_id.move_raw_ids.filtered(
                lambda m: m.state not in ('done', 'cancel') and float_compare(
                    m.quantity_done,
                    m.product_uom_qty,
                    precision_rounding=m.product_uom.rounding
                ) < 0
            ):
                for move_line in move.move_line_ids:
                    lines.append(
                        {
                            'move_id': move.id,
                            'qty_to_consume': move_line.product_uom_qty,
                            'qty_done': move_line.product_uom_qty,
                            'product_uom_id': move.product_uom.id,
                            'product_id': move.product_id.id,
                            'qty_reserved': move_line.product_uom_qty,
                        }
                    )

        self.produce_line_ids = [(5, )] + [(0, 0, x) for x in lines]
