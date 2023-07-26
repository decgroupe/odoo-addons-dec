# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021


from odoo import models
from odoo.tools import float_compare, float_is_zero


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _adjust_procure_method(self):
        super()._adjust_procure_method()
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for move in self.move_raw_ids.filtered(
            lambda x: x.procure_method != "make_to_order"
        ):
            product = move.product_id
            product_qty = move.product_uom_qty
            routes = (
                product.route_ids
                + product.route_from_categ_ids
                + move.warehouse_id.route_ids
            )
            mto_mts_rule = self.env["stock.rule"].search(
                [
                    ("route_id", "in", [x.id for x in routes]),
                    ("location_src_id", "=", move.location_id.id),
                    ("location_id", "=", move.location_dest_id.id),
                    ("action", "=", "split_procurement"),
                ],
                limit=1,
            )
            if mto_mts_rule:
                values = {}
                needed_qty = mto_mts_rule.get_mto_qty_to_order(
                    move.product_id, product_qty, move.product_uom, values
                )
                if float_is_zero(needed_qty, precision_digits=precision):
                    # No quantity is needed, keep existing stock move as is
                    pass
                elif (
                    float_compare(needed_qty, product_qty, precision_digits=precision)
                    == 0.0
                ):
                    # All quantity is needed, convert stock move in make to
                    # order
                    move.procure_method = "make_to_order"
                else:
                    # The existing stock move will be split in two
                    mto_move = move.copy({"procure_method": "make_to_order"})
                    mto_move.product_uom_qty = needed_qty
                    mts_move = move
                    mts_move.product_uom_qty = product_qty - needed_qty
