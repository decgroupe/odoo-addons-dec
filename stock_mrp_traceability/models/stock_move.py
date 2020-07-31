# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _

from ...stock_traceability.models.emoji_helper import (
    production_request_state_to_emoji,
)
from ...stock_traceability.models.html_helper import (
    format_hd,
)


class StockMove(models.Model):
    _inherit = "stock.move"

    pick_status = fields.Html(
        compute='_compute_pick_status',
        string='Picking Upstream Status',
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

    def _get_mto_status(self, html=False):
        res = []
        if self.created_mrp_production_request_id:
            head, desc = self._get_production_request_status(
                self.created_mrp_production_request_id
            )
            res.append(format_hd(head, desc, html))
        else:
            res.extend(super()._get_mto_status(html))
        return res

    def _get_mto_pick_status(self, html=False):
        return self._get_mto_status(html)

    def _get_mts_pick_status(self, html=False):
        return self._get_mts_status(html)

    def get_pick_status(self, upstream_move, html=False):
        status = []
        if self.procure_method == 'make_to_order':
            status = upstream_move._get_mto_pick_status(html)
        elif self.procure_method == 'make_to_stock':
            status = upstream_move._get_mts_pick_status(html)

        return upstream_move._format_status_header(status, html)

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
            upstream_move = move._get_upstream()
            if upstream_move and upstream_move.action_view_created_item_visible:
                move.pick_status = move.get_pick_status(
                    upstream_move, html=True
                )
            elif move.action_view_created_item_visible:
                move.pick_status = move.get_pick_status(move, html=True)
            else:
                move.pick_status = move.get_mrp_status(html=True)

    def action_view_created_item(self):
        self.ensure_one()
        if self.created_mrp_production_request_id:
            view = self.action_view_production_request(
                self.created_mrp_production_request_id.id
            )
        else:
            view = super().action_view_created_item()
            if not view:
                upstream_move = self._get_upstream()
                if upstream_move:
                    view = upstream_move.action_view_created_item()
        return view

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        res = self.created_mrp_production_request_id
        if not res:
            res = super().is_action_view_created_item_visible()
            if not res:
                upstream_move = self._get_upstream()
                if upstream_move:
                    res = upstream_move.is_action_view_created_item_visible()
        return res

    def action_view_production_request(self, id):
        action = self.env.ref(
            'mrp_production_request.mrp_production_request_action'
        ).read()[0]
        form = self.env.ref(
            'mrp_production_request.view_mrp_production_request_form'
        )
        action['views'] = [(form.id, 'form')]
        action['res_id'] = id
        return action