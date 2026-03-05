# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from collections import defaultdict

from odoo import Command, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _post_inventory(self, cancel_backorder=False):
        """Override to handle conservation of `consume_move_lines`."""
        consume_move_lines_per_order = defaultdict(lambda: self.env["stock.move.line"])
        for order in self:
            consume_move_lines_per_order[order] = order.move_finished_ids.mapped(
                "move_line_ids.consume_line_ids"
            )
        result = super()._post_inventory(cancel_backorder=cancel_backorder)
        # restore `consume_move_lines` previously linked to finished product move
        # lines, as super call may have changed them (using Command.set(...))
        for order in self:
            consume_move_lines = consume_move_lines_per_order[order]
            if consume_move_lines:
                order.move_finished_ids.move_line_ids.consume_line_ids = [
                    Command.link(ml.id) for ml in consume_move_lines
                ]
        return result

    def _post_inventory_consume(self, move_ids, cancel_backorder=False):
        """Post inventory for selected raw material moves and link consumed lines to
        finished product.
        This is a simplified version of `_post_inventory` that only processes selected
        moves (not all move_raw_ids) and links the resulting `move_line_ids` to the
        finished product via `consume_line_ids` for auditability.
        """
        self.ensure_one()
        # ignore moves already done
        moves_not_to_do = move_ids.filtered(lambda x: x.state == "done")
        # process only moves to do
        moves_to_do = move_ids.filtered(lambda x: x.state not in ("done", "cancel"))
        moves_to_do._action_done(cancel_backorder=cancel_backorder)
        # re-fetch moves after updated states to get the generated move lines
        moves = move_ids.filtered(lambda x: x.state == "done") - moves_not_to_do
        # link consume lines to finished product move lines for traceability
        consume_move_lines = moves.mapped("move_line_ids")
        if consume_move_lines:
            self.move_finished_ids.move_line_ids.consume_line_ids = [
                Command.link(ml.id) for ml in consume_move_lines
            ]
        return True

    def open_consume(self):
        """Open the consume wizard to manually consume raw materials."""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_production_consume.act_mrp_consume"
        )
        return action
