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
    production_state_to_emoji,
    purchase_state_to_emoji,
    stockmove_state_to_emoji,
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

    def _get_mto_mrp_status(self, html=False):
        res = []
        if self.created_purchase_line_id:
            p = self.created_purchase_line_id
            state = dict(p._fields['state']._description_selection(self.env)
                        ).get(p.state)
            head = '🛒{0}'.format(p.order_id.name)
            desc = '{0}{1}'.format(purchase_state_to_emoji(p.state), state)
            if html:
                res.append('{0} {1}'.format(head, small(desc)))
            else:
                res.append('{0} {1}'.format(head, desc))
        elif self.created_production_id:
            p = self.created_production_id
            state = dict(p._fields['state']._description_selection(self.env)
                        ).get(p.state)
            head = '⚙️{0}'.format(p.name)
            desc = '{0}{1}'.format(production_state_to_emoji(p.state), state)
            if html:
                res.append('{0} {1}'.format(head, small(desc)))
            else:
                res.append('{0} {1}'.format(head, desc))
        else:
            res.append('❓(???)[{0}]'.format(self.state))
        return res

    def _get_mts_mrp_status(self, html=False):
        res = []
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)

        head = '📦{0}'.format('Stock')
        desc = '{0}{1}'.format(stockmove_state_to_emoji(self.state), state)
        if html:
            res.append('{0} {1}'.format(head, small(desc)))
        else:
            res.append('{0} {1}'.format(head, desc))
        pre = False
        if self.created_purchase_line_archive and not self.created_purchase_line_id:
            pre = '♻️PO/'
        elif self.created_production_archive and not self.created_production_id:
            pre = '♻️MO/'
        if pre:
            res.append('{0}{1}'.format(pre, _('canceled')))
        return res

    def get_mrp_status(self, html=False):
        status = []
        if self.procure_method == 'make_to_order':
            status = self._get_mto_mrp_status(html)
        elif self.procure_method == 'make_to_stock':
            status = self._get_mts_mrp_status(html)

        product_type = dict(
            self._fields['product_type']._description_selection(self.env)
        ).get(self.product_type)

        head = '{0}{1}'.format(
            product_type_to_emoji(self.product_type),
            product_type,
        )
        if self.user_has_groups('base.group_no_one'):
            head = '{0} ({1})'.format(head, self.id)
        status.insert(0, head)
        if html:
            list_as_html = ''.join(list(map(li, status)))
            return div(ul(list_as_html), 'd_move d_move_' + self.state)
        else:
            return '\n'.join(status)

    @api.multi
    def _compute_mrp_status(self):
        for move in self:
            move.mrp_status = move.get_mrp_status(html=True)

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

    def action_view_picking(self):
        action = self.env.ref('mrp_traceability.stock_move_open_picking'
                             ).read()[0]
        form = self.env.ref('stock.view_picking_form')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = self.picking_id.id
        return action
