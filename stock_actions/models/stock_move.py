# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    action_reassign_visible = fields.Boolean(
        string="Shows button to reassign",
        compute="_compute_action_reassign_visible",
        readonly=True,
    )

    is_cancellable = fields.Boolean(
        compute="_compute_is_cancellable",
        help="Technical field to check for button visibility",
    )

    def _compute_action_reassign_visible(self):
        for move in self:
            visible = (
                move.quantity_done < move.product_uom_qty
                and not move.is_locked
                and move.state
                in ["confirmed", "waiting", "partially_available", "assigned"]
            )
            move.action_reassign_visible = visible

    @api.depends("procure_method", "state")
    def _compute_is_cancellable(self):
        self.is_cancellable = False
        for move in self:
            if move.procure_method == "make_to_stock":
                if move.state not in ("done", "cancel"):
                    move.is_cancellable = True
            if move.procure_method == "make_to_order":
                if move.state in ("draft"):
                    move.is_cancellable = True
                elif move.state in ("confirmed") and not move.move_orig_ids:
                    move.is_cancellable = True

    def action_confirm(self):
        """Inputs:
            - 'draft'
        Outputs:
            - 'confirmed'
            - 'waiting'
        """
        for move in self.filtered(lambda m: m.state in ["draft"]):
            move._action_confirm()

    def action_assign(self):
        """Inputs:
            - 'confirmed'
            - 'waiting'
            - 'partially_available'
        Outputs:
            - 'assigned'
            - 'partially_available'
        """
        for move in self:
            move._action_assign()

    def action_reassign(self):
        """Inputs:
            - 'assigned' --> unreserve --> 'confirmed'
            - 'partially_available' --> unreserve --> 'confirmed'
            - 'confirmed'
            - 'waiting'
            - 'partially_available'
        Outputs:
            - 'assigned'
            - 'partially_available'
        """
        for move in self:
            move._do_unreserve()
            move._action_assign()

    def action_recompute_state(self):
        self._recompute_state()

    def action_force_state_confirmed_to_assigned(self):
        for move in self.filtered(lambda m: m.state == "confirmed"):
            move.write({"state": "assigned"})

    def _action_cancel_stream(self, downstream=False, upstream=False):
        def get_downstream_moves(move):
            res = move
            if move and move.move_dest_ids:
                for m in move.move_dest_ids:
                    if move.product_id.id == m.product_id.id:
                        res += get_downstream_moves(m)
            return res

        def get_upstream_moves(move):
            res = move
            if move and move.move_orig_ids:
                for m in move.move_orig_ids:
                    if move.product_id.id == m.product_id.id:
                        res += get_upstream_moves(m)
            return res

        moves_to_cancel = self.env["stock.move"]
        for move in self:
            moves_to_cancel += move
            if downstream:
                moves_to_cancel += get_downstream_moves(move)
            if upstream:
                moves_to_cancel += get_upstream_moves(move)

        moves_to_cancel = moves_to_cancel.filtered(
            lambda x: x.state not in ("done", "cancel")
        )
        if moves_to_cancel:
            moves_to_cancel._action_cancel()

    def action_cancel(self):
        """Inputs:
            - 'assigned' --> unreserve --> 'confirmed'
            - 'partially_available' --> unreserve --> 'confirmed'
            - 'confirmed'
        Outputs:
            - 'cancel'
        """
        self._action_cancel_stream()

    def action_cancel_downstream(self):
        self._action_cancel_stream(downstream=True)

    def action_cancel_upstream(self):
        self._action_cancel_stream(upstream=True)

    def action_done(self):
        """Inputs:
            - 'draft' --> confirm --> 'confirmed'
            - 'product_uom_qty' == 'quantity_done'
        Outputs:
            - 'done'
        """
        self._action_done()
