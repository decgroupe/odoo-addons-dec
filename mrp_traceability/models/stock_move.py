# -*- coding: utf-8 -*-
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

from odoo import api, fields, models, _
from .emoji_helper import (
    production_to_emoji,
    purchase_to_emoji,
    stockmove_to_emoji,
    product_type_to_emoji,
)
from .html_helper import (div, ul, li, small)


class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_status = fields.Html(
        compute='_compute_mrp_status',
        string='Procurement status',
        default='',
        store=False,
    )

    def _get_mto_mrp_status(self, move):
        if move.created_purchase_line_id:
            p = move.created_purchase_line_id
            state = dict(p._fields['state']._description_selection(self.env)
                        ).get(p.state)
            res = li('🛒{0} ' + small('{1}{2}')).format(
                p.order_id.name,
                purchase_to_emoji(p),
                state,
            )
        elif move.created_production_id:
            p = move.created_production_id
            state = dict(p._fields['state']._description_selection(self.env)
                        ).get(p.state)
            res = li('⚙️{0} ' + small('{1}{2}')).format(
                p.name,
                production_to_emoji(p),
                state,
            )
        else:
            res = li('❓(???)[{0}]').format(move.state)
        return res

    def _get_mts_mrp_status(self, move):
        #procure_method = dict(move._fields['procure_method']._description_selection(self.env)).get(move.procure_method)
        procure_method = 'Stock'
        state = dict(move._fields['state']._description_selection(self.env)
                    ).get(move.state)
        res = li('📦{0} ' + small('{1}{2}')).format(
            procure_method,
            stockmove_to_emoji(move),
            state,
        )
        pre = False
        if move.created_purchase_line_archive and not move.created_purchase_line_id:
            pre = '♻️PO/'
        elif move.created_production_archive and not move.created_production_id:
            pre = '♻️MO/'
        if pre:
            res = ('{0}' + li('{1}{2}')).format(res, pre, _('canceled'))
        return res

    @api.multi
    def _compute_mrp_status(self):
        for move in self:
            res = '...'
            if move.procure_method == 'make_to_order':
                res = self._get_mto_mrp_status(move)
            elif move.procure_method == 'make_to_stock':
                res = self._get_mts_mrp_status(move)

            product_type = dict(
                move._fields['product_type']._description_selection(self.env)
            ).get(move.product_type)

            head = '{0}{1} ({2})'.format(
                product_type_to_emoji(move.product_type),
                product_type,
                move.id,
            )
            status = ul('{0}{1}').format(li(head), res)
            move.mrp_status = div(status, 'd_move d_move_' + move.state)

    def action_view_created_item(self):
        self.ensure_one()
        if self.created_purchase_line_id:
            return self.action_view_created_purchase()
        elif self.created_production_id:
            return self.action_view_created_production()

    def action_view_created_purchase(self):
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        form = self.env.ref('purchase.purchase_order_form')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = self.created_purchase_line_id.order_id.id
        return action

    def action_view_created_production(self):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        form = self.env.ref('mrp.mrp_production_form_view')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = self.created_production_id.id
        return action
