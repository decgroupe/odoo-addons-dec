# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020

from odoo import models, api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.multi
    def action_propagate_cancel(self):
        def recursive_cancel(move):
            res = self.env['stock.move']
            if move:
                res += move
                if move.move_dest_ids:
                    for m in move.move_dest_ids:
                        if move.product_id == m.product_id:
                            res += recursive_cancel(m)
            return res

        if self.env.context.get('propagate'):
            moves_to_cancel = self.env['stock.move']
            for line in self:
                for move in line.move_dest_ids:
                    moves_to_cancel += recursive_cancel(move)

            moves_to_cancel = moves_to_cancel.filtered(
                lambda x: x.state not in ('done', 'cancel')
            )
            if moves_to_cancel:
                moves_to_cancel._action_cancel()

        # Keep a link with orders
        purchase_orders = self.env['purchase.order']
        for line in self:
            purchase_orders |= line.order_id
        # Finally delete all
        self.unlink()
        # Cancel empty orders
        for order in purchase_orders:
            if not order.order_line:
                order.button_cancel()
        # Close current form and reload
        return self.action_close_dialog()

    @api.multi
    def action_close_dialog(self):
        self.ensure_one()
        # OCA module needed: web_ir_actions_act_view_reload
        view = {
            'type': 'ir.actions.act_view_reload',
        }
        return view
