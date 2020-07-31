# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import logging

from odoo import api, fields, models

from ...stock_traceability.models.html_helper import (
    format_hd,
)

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

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

    def _get_mts_status(self, html=False):
        res = super()._get_mts_status(html)

        for p in self.orderpoint_created_production_ids:
            head, desc = self._get_production_status(p)
            res.append(format_hd('♻️⮡ ' + head, desc, html))

        for p in self.orderpoint_created_purchase_line_ids:
            head, desc = self._get_purchase_status(p)
            res.append(format_hd('♻️⮡ ' + head, desc, html))

        return res

    def action_view_created_item(self):
        self.ensure_one()
        view = super().action_view_created_item()
        if not view:
            if self.orderpoint_created_purchase_line_ids:
                view = self.action_view_purchase(
                    self.orderpoint_created_purchase_line_ids[0].order_id.id
                )
            elif self.orderpoint_created_production_ids:
                view = self.action_view_production(
                    self.orderpoint_created_production_ids.ids[0]
                )
        return view

    def is_action_view_created_item_visible(self):
        res = super().is_action_view_created_item_visible()
        if not res:
            res = self.orderpoint_created_purchase_line_ids \
                or self.orderpoint_created_production_ids
        return res
