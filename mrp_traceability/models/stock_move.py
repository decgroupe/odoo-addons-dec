# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020

from odoo import api, fields, models, _
from .emoji_helper import (
    production_state_to_emoji,
    purchase_state_to_emoji,
    stockmove_state_to_emoji,
    product_type_to_emoji,
)
from .html_helper import (div, ul, li, small, format_hd)


class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_status = fields.Html(
        compute='_compute_mrp_status',
        string='Procurement status',
        default='',
        store=False,
    )
    orderpoint_created_production_ids = fields.Many2many(
        'mrp.production',
        'Created Production Orders by Orderpoint',
        compute='_compute_orderpoint_created_orders',
    )
    orderpoint_created_purchase_line_ids = fields.Many2many(
        'purchase.order.line',
        'Created Purchase Order Lines by Orderpoint',
        compute='_compute_orderpoint_created_orders',
    )

    def _get_production_status(self, production_id):
        p = production_id
        state = dict(p._fields['state']._description_selection(self.env)).get(
            p.state
        )
        head = '⚙️{0}'.format(p.name)
        desc = '{0}{1}'.format(production_state_to_emoji(p.state), state)
        return head, desc

    def _get_purchase_status(self, purchase_line_id):
        p = purchase_line_id
        state = dict(p._fields['state']._description_selection(self.env)).get(
            p.state
        )
        head = '🛒{0}'.format(p.order_id.name)
        desc = '{0}{1}'.format(purchase_state_to_emoji(p.state), state)
        return head, desc

    def _get_stock_status(self):
        state = dict(self._fields['state']._description_selection(self.env)
                    ).get(self.state)
        head = '📦{0}'.format('Stock')
        if self.procure_method == 'make_to_order':
            head = '❓{0}'.format(_(self.procure_method))
        desc = '{0}{1}'.format(stockmove_state_to_emoji(self.state), state)
        return head, desc

    def _get_mto_mrp_status(self, html=False):
        res = []
        if self.created_purchase_line_id:
            head, desc = self._get_purchase_status(
                self.created_purchase_line_id
            )
            res.append(format_hd(head, desc, html))
        elif self.created_production_id:
            head, desc = self._get_production_status(self.created_production_id)
            res.append(format_hd(head, desc, html))
        else:
            res.append('❓(???)[{0}]'.format(self.state))
            # Since the current status is unknown, fallback using mts status
            # to print archive when exists
            res.extend(self._get_mts_mrp_status(html))
        return res

    def _get_mts_mrp_status(self, html=False):
        res = []

        head, desc = self._get_stock_status()
        res.append(format_hd(head, desc, html))

        pre = False
        if self.created_purchase_line_archive and not self.created_purchase_line_id:
            pre = '♻️PO/'
        elif self.created_production_archive and not self.created_production_id:
            pre = '♻️MO/'
        if pre:
            res.append('{0}{1}'.format(pre, _('canceled')))

        for p in self.orderpoint_created_production_ids:
            head, desc = self._get_production_status(p)
            res.append(format_hd('♻️⮡ ' + head, desc, html))

        for p in self.orderpoint_created_purchase_line_ids:
            head, desc = self._get_purchase_status(p)
            res.append(format_hd('♻️⮡ ' + head, desc, html))

        return res

    def _format_status_header(self, status, html=False):
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

    def get_mrp_status(self, html=False):
        status = []
        if self.procure_method == 'make_to_order':
            status = self._get_mto_mrp_status(html)
        elif self.procure_method == 'make_to_stock':
            status = self._get_mts_mrp_status(html)

        return self._format_status_header(status, html)

    @api.multi
    @api.depends(
        'procure_method',
        'product_type',
        'created_purchase_line_id',
        'created_production_id',
    )
    def _compute_mrp_status(self):
        for move in self:
            move.mrp_status = move.get_mrp_status(html=True)

    @api.multi
    def _compute_orderpoint_created_orders(self):
        Orderpoint = self.env['stock.warehouse.orderpoint']
        Production = self.env['mrp.production']
        PurchaseLine = self.env['purchase.order.line']
        for move in self:
            move.orderpoint_created_production_ids = False
            move.orderpoint_created_purchase_line_ids = False
            if move.procure_method == 'make_to_stock' and move.state == 'confirmed':
                reordering_rules = Orderpoint.search(
                    [('product_id', '=', move.product_id.id)]
                )
                if reordering_rules.ids:
                    # Search for production orders created by mts rules
                    move.orderpoint_created_production_ids = \
                        Production.search(
                            [('orderpoint_id', 'in', reordering_rules.ids)]
                        )
                    # Search for purchase orders created by mts rules
                    move.orderpoint_created_purchase_line_ids = \
                        PurchaseLine.search(
                            [('orderpoint_ids', 'in', reordering_rules.ids)]
                        )

    def action_view_created_item(self):
        self.ensure_one()
        if self.created_purchase_line_id:
            return self.action_view_purchase(
                self.created_purchase_line_id.order_id.id
            )
        elif self.created_production_id:
            return self.action_view_production(self.created_production_id.id)
        elif self.orderpoint_created_purchase_line_ids:
            return self.action_view_purchase(
                self.orderpoint_created_purchase_line_ids[0].order_id.id
            )
        elif self.orderpoint_created_production_ids:
            return self.action_view_production(
                self.orderpoint_created_production_ids.ids[0]
            )

    def action_view_purchase(self, id):
        action = self.env.ref('purchase.purchase_form_action').read()[0]
        form = self.env.ref('purchase.purchase_order_form')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action

    def action_view_production(self, id):
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        form = self.env.ref('mrp.mrp_production_form_view')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action

    def action_view_picking(self):
        action = self.env.ref('mrp_traceability.stock_move_open_picking'
                             ).read()[0]
        form = self.env.ref('stock.view_picking_form')
        action['views'] = [(form.id, 'form')]
        action['res_id'] = self.picking_id.id
        return action
