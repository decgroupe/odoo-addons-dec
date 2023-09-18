# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import models
from odoo.tools import float_round


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    """ This is a light copy of `_post_inventory`. Code related to finish_moves has
    been removed and we can select which moves will be processed instead of
    `order.move_raw_ids`
    """

    def _post_inventory_consume(self, move_ids, cancel_backorder=False):
        self.ensure_one()
        order = self
        moves_not_to_do = move_ids.filtered(lambda x: x.state == "done")
        moves_to_do = move_ids.filtered(lambda x: x.state not in ("done", "cancel"))
        for move in moves_to_do.filtered(
            lambda m: m.product_qty == 0.0 and m.quantity_done > 0
        ):
            move.product_uom_qty = move.quantity_done
        # MRP do not merge move, catch the result of _action_done in order
        # to get extra moves.
        moves_to_do = moves_to_do._action_done(cancel_backorder=cancel_backorder)
        moves_to_do = move_ids.filtered(lambda x: x.state == "done") - moves_not_to_do
        consume_move_lines = moves_to_do.mapped("move_line_ids")
        order.move_finished_ids.move_line_ids.consume_line_ids = [
            (6, 0, consume_move_lines.ids)
        ]
        return True

    def open_consume(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_production_consume.act_mrp_consume"
        )
        return action
