# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging

from odoo import _, api, fields, models

from odoo.addons.tools_miscellaneous.tools.html_helper import (
    format_hd,
    div,
)

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    orderpoint_created_production_ids = fields.Many2many(
        comodel_name='mrp.production',
        compute='_compute_orderpoint_created_orders',
        string='Created Production Orders by Orderpoint',
    )
    orderpoint_created_purchase_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        compute='_compute_orderpoint_created_orders',
        string='Created Purchase Order Lines by Orderpoint',
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

        production_ids = self.orderpoint_created_production_ids.filtered(
            lambda p: p.state not in ('done', 'cancel')
        )
        if production_ids:
            for p in self.production_ids:
                head, desc = p.get_head_desc()
                res.append(format_hd('♻️⮡ ' + head, desc, html))
        # else:
        #     head = '⚠️{0}'.format(_('Orderpoint issue'))
        #     desc = '\n' + _('No production order in progress')
        #     hd = format_hd(head, desc, html)
        #     if html:
        #         hd = div(hd, 'alert-warning')
        #     res.append(hd)

        purchase_line_ids = self.orderpoint_created_purchase_line_ids.filtered(
            lambda p: p.state not in ('done', 'cancel')
        )
        if purchase_line_ids:
            for p in purchase_line_ids:
                head, desc = p.get_head_desc()
                res.append(format_hd('♻️⮡ ' + head, desc, html))
        # else:
        #     head = '⚠️{0}'.format(_('Orderpoint issue'))
        #     desc = '\n' + _('No purchase order in progress')
        #     hd = format_hd(head, desc, html)
        #     if html:
        #         hd = div(hd, 'alert-warning')
        #     res.append(hd)

        return res

    def action_view_created_item(self):
        self.ensure_one()
        action = super().action_view_created_item()
        if not action:
            if self.orderpoint_created_purchase_line_ids:
                action = self.orderpoint_created_purchase_line_ids.action_view()
            elif self.orderpoint_created_production_ids:
                action = self.orderpoint_created_production_ids.action_view()
        return action

    def is_action_view_created_item_visible(self):
        res = super().is_action_view_created_item_visible()
        if not res:
            res = self.orderpoint_created_purchase_line_ids \
                or self.orderpoint_created_production_ids
        return res
