# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Sep 2020

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
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

        moves_to_cancel = self.env['stock.move']
        for move in self:
            moves_to_cancel += move
            if downstream:
                moves_to_cancel += get_downstream_moves(move)
            if upstream:
                moves_to_cancel += get_upstream_moves(move)

        moves_to_cancel = moves_to_cancel.filtered(
            lambda x: x.state not in ('done', 'cancel')
        )
        if moves_to_cancel:
            moves_to_cancel._action_cancel()

    @api.multi
    def action_cancel(self):
        self._action_cancel_stream()

    @api.multi
    def action_cancel_downstream(self):
        self._action_cancel_stream(downstream=True)

    @api.multi
    def action_cancel_upstream(self):
        self._action_cancel_stream(upstream=True)
