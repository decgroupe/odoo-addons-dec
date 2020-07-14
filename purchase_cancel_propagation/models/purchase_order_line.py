# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Apr 2020

from odoo import fields, models, api


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

        # Finally delete all
        self.unlink()
        # Close current form and reload
        return self.action_close_dialog()

    @api.multi
    def action_close_dialog(self):
        self.ensure_one()
        # OCA module needed: web_ir_actions_act_view_reload
        view =  {
            'type': 'ir.actions.act_view_reload',
        }
        return view
