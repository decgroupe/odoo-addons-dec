# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import models
from odoo.tools import float_compare, float_is_zero


class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self, picking_type_code=False):
        """Extend procure method adjustment to handle split_procurement rules.

        After the base logic runs (which sets split_procurement moves to
        make_to_stock), re-evaluate those moves against the MTS+MTO rule and
        convert them to make_to_order or split them when required.
        """
        ids_to_super = set()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self:
            if move.procure_method == "make_to_order":
                ids_to_super.add(move.id)
                continue
            product = move.product_id
            product_qty = move.product_uom_qty
            routes = (
                product.route_ids
                + product.route_from_categ_ids
                + move.warehouse_id.route_ids
            )
            mto_mts_rule = self.env["stock.rule"].search(
                [
                    ("route_id", "in", routes.ids),
                    ("location_src_id", "=", move.location_id.id),
                    ("location_dest_id", "=", move.location_dest_id.id),
                    ("action", "=", "split_procurement"),
                ],
                limit=1,
            )
            if not mto_mts_rule:
                ids_to_super.add(move.id)
                continue
            values = {}
            needed_qty = mto_mts_rule.get_mto_qty_to_order(
                move.product_id, product_qty, move.product_uom, values
            )
            if float_is_zero(needed_qty, precision_digits=precision):
                # no quantity is needed, keep existing stock move as is and do not call
                # super otherwise it would be set to `make_to_order` by the base logic
                continue
            elif (
                float_compare(needed_qty, product_qty, precision_digits=precision)
                == 0.0
            ):
                # all quantity is needed, convert stock move to make_to_order
                move.procure_method = "make_to_order"
            else:
                # the existing stock move will be split in two
                mto_move = move.copy({"procure_method": "make_to_order"})
                mto_move.product_uom_qty = needed_qty
                mts_move = move
                mts_move.product_uom_qty = product_qty - needed_qty
        return super(StockMove, self.browse(ids_to_super))._adjust_procure_method(
            picking_type_code=picking_type_code
        )
