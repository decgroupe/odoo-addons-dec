# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mrp_status = fields.Html(
        compute="_compute_mrp_status",
        string="Manufacturing Upstream Status",
        default="",
        store=False,
    )

    def _get_mto_mrp_status(self, html=False):
        return self._get_mto_status(html)

    def _get_mts_mrp_status(self, html=False):
        return self._get_mts_status(html)

    def get_mrp_status(self, html=False):
        status = []
        if self.procure_method == "make_to_order":
            status = self._get_mto_mrp_status(html)
        elif self.procure_method == "make_to_stock":
            status = self._get_mts_mrp_status(html)

        status += self._get_assignable_status(html)
        return self._format_status_header(status, html)

    @api.depends(
        "procure_method",
        "product_type",
        "created_purchase_line_id",
        "created_production_id",
    )
    def _compute_mrp_status(self):
        for move in self:
            move.mrp_status = move.get_mrp_status(html=True)

    def action_view_created_item(self):
        self.ensure_one()
        view = super().action_view_created_item()
        if not view:
            pass
        return view

    def is_action_view_created_item_visible(self):
        self.ensure_one()
        res = super().is_action_view_created_item_visible()
        if not res:
            pass
        return res

    def action_view_picking(self):
        action = self.env.ref("mrp_traceability.stock_move_open_picking").read()[0]
        form = self.env.ref("stock.view_picking_form")
        action["views"] = [(form.id, "form")]
        action["res_id"] = self.picking_id.id
        return action
