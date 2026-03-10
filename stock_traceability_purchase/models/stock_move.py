# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    created_purchase_lines_archive = fields.Json(
        readonly=True,
        copy=False,
    )

    def _archive_created_purchase_lines(self):
        # should operate only if created_purchase_line_ids` has been edited
        self.ensure_one()
        archive = self.created_purchase_lines_archive or {}
        for created_purchase_line_id in self.created_purchase_line_ids:
            if created_purchase_line_id.id not in archive:
                archive[created_purchase_line_id.id] = (
                    created_purchase_line_id.order_id.name
                )
        self.created_purchase_lines_archive = archive

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            if "created_purchase_line_ids" in vals:
                rec._archive_created_purchase_lines()
        return record_ids

    def write(self, values):
        res = super().write(values)
        if "created_purchase_line_ids" in values:
            for rec in self:
                rec._archive_created_purchase_lines()
        return res

    @api.depends(
        "procure_method",
        "created_purchase_line_ids",
        "move_orig_ids.purchase_line_id",
    )
    def _compute_pick_status(self):
        return super()._compute_pick_status()

    def _get_mts_pre_archive(self):
        pre = super()._get_mts_pre_archive()
        if self.created_purchase_lines_archive and not self.created_purchase_line_ids:
            pre = "♻️PO/"
        return pre

    def _get_mto_created_items(self):
        res = super()._get_mto_created_items()
        if self.created_purchase_line_ids:
            action = self.created_purchase_line_ids.mapped("order_id").action_view()
            res["stock_traceability_purchase"] = {
                "priority": 50,
                "record": self.created_purchase_line_ids,
                "action": action,
            }
        elif self.move_orig_ids.purchase_line_id:
            action = self.move_orig_ids.purchase_line_id.order_id.action_view()
            res["stock_traceability_purchase"] = {
                "priority": 50,
                "record": self.move_orig_ids.purchase_line_id,
                "action": action,
            }
        # add this case even if it should not happen since a `purchase_line_id` is only
        # set for a `make_to_stock` move
        elif self.purchase_line_id:
            action = self.purchase_line_id.order_id.action_view()
            res["stock_traceability_purchase"] = {
                "priority": 50,
                "record": self.purchase_line_id,
                "action": action,
            }
        return res
