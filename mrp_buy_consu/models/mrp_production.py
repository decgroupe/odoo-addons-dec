# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_raw_moves(self, exploded_lines):
        moves = super()._generate_raw_moves(exploded_lines)
        return moves

    def _generate_raw_move(self, bom_line, line_data):
        move = super()._generate_raw_move(bom_line, line_data)
        return move

    def _get_raw_move_data(self, bom_line, line_data):
        res = super()._get_raw_move_data(bom_line, line_data)
        if res is not None:
            if bom_line.product_id.is_consumable:
                # Check this bom line if this product MUST be
                # purchased (using buy_consumable boolean)
                if bom_line.buy_consumable:
                    res['procure_method'] = 'make_to_order'
                else:
                    # Override source location if product is consumable
                    # Copy destination to source location to create a fake
                    # move that will stay in Warehouse/Production location
                    location = self.env['stock.location'].browse(
                        res['location_dest_id']
                    )
                    res['location_id'] = location.id
                    res['warehouse_id'] = location.get_warehouse().id
        return res
