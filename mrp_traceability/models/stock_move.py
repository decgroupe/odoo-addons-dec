# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

import logging

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    move_conv_dest_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_move_conv_rel",
        column1="move_conv_orig_id",
        column2="move_conv_dest_id",
        string="Destination Moves (After Conversion)",
        copy=False,
        help="Optional: final stock move when building a product",
    )
    move_conv_orig_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_move_conv_rel",
        column1="move_conv_dest_id",
        column2="move_conv_orig_id",
        string="Original Moves (Before Conversion)",
        copy=False,
        help="Optional: raw stock moves when building a product",
    )

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
        "move_orig_ids.purchase_line_id",
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
        action = self.env["ir.actions.actions"]._for_xml_id(
            "mrp_traceability.stock_move_open_picking"
        )
        form = self.env.ref("stock.view_picking_form")
        action["views"] = [(form.id, "form")]
        action["res_id"] = self.picking_id.id
        return action

    def _migrate_dest_move_to_conv_dest_move(self):
        domain = [
            ("production_id", "!=", False),
        ]
        production_move_ids = (
            self.env["stock.move"]
            .with_context(prefetch_fields=False)
            .search(domain, limit=0)
        )

        for production_move_id in production_move_ids:
            production_id = production_move_id.production_id
            if production_move_id.move_conv_orig_ids:
                continue
            if not production_id.move_raw_ids and not production_move_id.move_orig_ids:
                continue
            if production_id.bom_id:
                bom_name = production_id.bom_id.name_get()[0][1]
            else:
                bom_name = "???"
            _logger.info(
                "Processing %s %s %s"
                % (production_id.name, production_id.state, bom_name)
            )
            raw_move_ids = production_move_id.move_orig_ids
            if (
                production_move_id.product_id.id
                in raw_move_ids.mapped("product_id").ids
            ):
                raise ValidationError("Possible invalid data (same product)")
            if len(production_id.move_raw_ids) != len(raw_move_ids):
                if len(raw_move_ids) == 0 and production_id.state == "cancel":
                    # Ok relink
                    pass
                elif len(production_id.move_raw_ids) > len(raw_move_ids):
                    diff_move_ids = production_id.move_raw_ids - raw_move_ids
                    if diff_move_ids.mapped("state") == "cancel":
                        # ok Relink + re-attach
                        pass
                else:
                    raise ValidationError("Possible invalid data (raw count)")

            production_move_id.move_conv_orig_ids = production_id.move_raw_ids
            production_move_id.move_orig_ids = False
