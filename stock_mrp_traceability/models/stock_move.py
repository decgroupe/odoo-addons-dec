# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models, _

from odoo.addons.tools_miscellaneous.tools.html_helper import (
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

    def _get_mto_status(self, html=False):
        res = []
        if self.created_mrp_production_request_id:
            head, desc = self.created_mrp_production_request_id.get_head_desc()
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

        if self.picking_code == 'incoming':
            for group_id in self.move_dest_ids.mapped('group_id'):
                head, desc = group_id.get_head_desc()
                head += '📥'
                status.append(format_hd(head, desc, html))

        if self.picking_code == 'outgoing':
            for group_id in self.move_orig_ids.mapped('group_id'):
                head, desc = group_id.get_head_desc()
                head += '📤'
                status.append(format_hd(head, desc, html))

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
                action = self.created_mrp_production_request_id.\
                    action_view_mrp_productions()
            else:
                action = self.created_mrp_production_request_id.action_view()
        else:
            action = super().action_view_created_item()
        return action

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        res = self.created_mrp_production_request_id
        if not res:
            res = super().is_action_view_created_item_visible()
        return res
