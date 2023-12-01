# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    def _get_move_raw_values(
        self,
        product_id,
        product_uom_qty,
        product_uom,
        operation_id=False,
        bom_line=False,
    ):
        res = super(MrpProduction, self)._get_move_raw_values(
            product_id, product_uom_qty, product_uom, operation_id, bom_line
        )
        if res is not None:
            if bom_line.product_id.is_consumable:
                # Check this bom line if this product MUST be
                # purchased (using buy_consumable boolean)
                if bom_line.buy_consumable:
                    res["procure_method"] = "make_to_order"
                else:
                    # Override source location if product is consumable
                    # Copy destination to source location to create a fake
                    # move that will stay in Warehouse/Production location
                    location = self.env["stock.location"].browse(
                        res["location_dest_id"]
                    )
                    res["location_id"] = location.id
                    res["warehouse_id"] = location.get_warehouse().id
        return res

    @api.onchange("location_src_id", "move_raw_ids", "bom_id")
    def _onchange_location(self):
        """Inherit `onchange` since values set in `_get_move_raw_values` will be
        overriden by this function"""
        super()._onchange_location()
        for move in self.move_raw_ids:
            if move.product_id.is_consumable and not move.bom_line_id.buy_consumable:
                move.location_id = move.location_dest_id
                move.warehouse_id = move.location_dest_id.get_warehouse()
