# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2023

from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        """Exclude consumable move to buy"""
        ids_to_super = set()
        for move in self:
            # Check this bom line if this product MUST be
            # purchased (using buy_consumable boolean)
            if (
                move.bom_line_id.product_id.is_consumable
                and move.bom_line_id.buy_consumable
            ):
                move.procure_method = "make_to_order"
            else:
                ids_to_super.add(move.id)
        return super(StockMove, self.browse(ids_to_super))._adjust_procure_method()

    @api.depends(
        "bom_line_id",
        "bom_line_id.product_id.is_consumable",
        "bom_line_id.buy_consumable",
        "location_dest_id",
    )
    def _compute_location_id(self):
        ids_to_super = set()
        for move in self:
            if (
                move.bom_line_id
                and move.bom_line_id.product_id.is_consumable
                and not move.bom_line_id.buy_consumable
            ):
                # enforce same location for source and destination
                location = move.location_dest_id
                move.location_id = location
                move.warehouse_id = location.warehouse_id.id
            else:
                ids_to_super.add(move.id)
        return super(StockMove, self.browse(ids_to_super))._compute_location_id()
