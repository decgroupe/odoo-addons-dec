# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _

from ...mrp_traceability.models.emoji_helper import (
    production_state_to_emoji,
    production_request_state_to_emoji,
    purchase_state_to_emoji,
    stockmove_state_to_emoji,
    product_type_to_emoji,
)
from ...mrp_traceability.models.html_helper import (
    div, ul, li, small, format_hd
)


class StockMove(models.Model):
    _inherit = "stock.move"

    pick_status = fields.Html(
        compute='_compute_pick_status',
        string='Procurement status ',
        default='',
        store=False,
    )

    def _get_production_request_status(self, request_id):
        r = request_id
        state = dict(r._fields['state']._description_selection(self.env)).get(
            r.state
        )
        head = '🗃️{0}'.format(r.name)
        desc = '{0}{1}'.format(
            production_request_state_to_emoji(r.state), state
        )
        return head, desc

    def _get_mto_pick_status(self, html=False):
        res = []
        if self.created_purchase_line_id:
            head, desc = self._get_purchase_status(
                self.created_purchase_line_id
            )
            res.append(format_hd(head, desc, html))
        elif self.created_mrp_production_request_id:
            head, desc = self._get_production_request_status(
                self.created_mrp_production_request_id
            )
            res.append(format_hd(head, desc, html))
        elif self.production_id:
            head, desc = self._get_production_status(self.production_id)
            res.append(format_hd(head, desc, html))
        else:
            res.append('❓(???)[{0}]'.format(self.state))
            # Since the current status is unknown, fallback using mts status
            # to print archive when exists
            res.extend(self._get_mts_pick_status(html))
        return res

    def _get_mts_pick_status(self, html=False):
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

    def get_pick_status(self, upstream_move, html=False):
        status = []
        if self.procure_method == 'make_to_order':
            status = upstream_move._get_mto_pick_status(html)
        elif self.procure_method == 'make_to_stock':
            status = upstream_move._get_mts_pick_status(html)

        return self._format_status_header(status, html)

    def _is_related(self):
        if self.created_purchase_line_id \
            or self.created_mrp_production_request_id \
            or self.production_id:
            return True
        else:
            return False

    @api.multi
    @api.depends(
        'procure_method',
        'product_type',
        'created_purchase_line_id',
        'move_orig_ids.production_id',
    )
    def _compute_pick_status(self):
        for move in self:
            upstream_move = move.move_orig_ids and move.move_orig_ids[0] or False
            if upstream_move and upstream_move._is_related():
                move.pick_status = move.get_pick_status(
                    upstream_move, html=True
                )
            elif move._is_related():
                move.pick_status = move.get_pick_status(move, html=True)
            else:
                move.pick_status = move.get_mrp_status(html=True)
