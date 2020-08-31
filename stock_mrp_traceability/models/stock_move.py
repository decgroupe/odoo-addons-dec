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
        r = request_id.sudo()
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

    def get_pick_status(self, html=False):
        status = []
        if self.procure_method == 'make_to_order':
            status += self._get_mto_pick_status(html)
        elif self.procure_method == 'make_to_stock':
            status += self._get_mts_pick_status(html)

        upstream_moves = self._get_upstreams()
        for move in upstream_moves:
            upstream_status = []
            if self.procure_method == 'make_to_order':
                upstream_status += move._get_mto_pick_status(html)
            elif self.procure_method == 'make_to_stock':
                upstream_status += move._get_mts_pick_status(html)
            # Check if status is not a duplicate, it could happen in some
            # cases where we can have self.created_production_id identical to
            # move.production_id
            for upstream_status_line in upstream_status:
                if upstream_status_line not in status:
                    status.append(upstream_status_line)

        status += self._get_assignable_status(html)
        return self._format_status_header(status, html)

    def _is_related(self):
        if self.created_purchase_line_id \
            or self.purchase_line_id \
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
            if move.action_view_created_item_visible:
                move.pick_status = move.get_pick_status(html=True)
            else:
                move.pick_status = move.get_mrp_status(html=True)

    def action_view_created_item(self):
        if self.created_mrp_production_request_id:
            if self.created_mrp_production_request_id.mrp_production_ids:
                view = self.created_mrp_production_request_id.\
                    action_view_mrp_productions()
            else:
                view = self.action_view_production_request(
                    self.created_mrp_production_request_id.id
                )
        else:
            view = super().action_view_created_item()
        return view

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        res = self.created_mrp_production_request_id
        if not res:
            res = super().is_action_view_created_item_visible()
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
