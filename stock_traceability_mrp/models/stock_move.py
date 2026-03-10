# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    mrp_status = fields.Html(
        compute="_compute_mrp_status",
        string="Manufacturing Upstream Status",
        default="",
        store=False,
    )
    created_productions_archive = fields.Json(
        readonly=True,
        copy=False,
    )

    def _archive_created_productions(self):
        # should operate only if created_production_id` has been edited
        self.ensure_one()
        archive = self.created_productions_archive or {}
        if self.created_production_id and self.created_production_id.id not in archive:
            archive[self.created_production_id.id] = self.created_production_id.name
        self.created_productions_archive = archive

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            if "created_production_id" in vals:
                rec._archive_created_productions()
        return record_ids

    def write(self, values):
        res = super().write(values)
        if "created_production_id" in values:
            for rec in self:
                rec._archive_created_productions()
        return res

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
        "created_production_id",
    )
    def _compute_mrp_status(self):
        for move in self:
            move.mrp_status = move.get_mrp_status(html=True)

    @api.depends(
        "procure_method",
        "move_orig_ids.production_id",
    )
    def _compute_pick_status(self):
        res = super()._compute_pick_status()
        for move in self:
            if not move.action_view_created_item_visible:
                move.pick_status = move.get_mrp_status(html=True)
        return res

    def _get_mts_pre_archive(self):
        pre = super()._get_mts_pre_archive()
        # contrary to `purchase` module, `created_production_id` is not unset when
        # the production order is cancel, so we have to check for both states
        if self.created_productions_archive and (
            not self.created_production_id
            or self.created_production_id.state == "cancel"
        ):
            pre = "♻️MO/"
        return pre

    def _get_mto_created_items(self):
        res = super()._get_mto_created_items()
        if self.created_production_id:
            action = self.created_production_id.action_view()
            res["stock_traceability_mrp"] = {
                "priority": 30,
                "record": self.created_production_id,
                "action": action,
            }
        # add this case even if it should not happen since a `production_id` is only
        # set for a `make_to_stock` move
        elif self.production_id:
            action = self.production_id.action_view()
            res["stock_traceability_mrp"] = {
                "priority": 30,
                "record": self.production_id,
                "action": action,
            }
        return res
