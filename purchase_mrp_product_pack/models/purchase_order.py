# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _create_picking(self):
        self._create_pack_stock_moves()
        res = super()._create_picking()
        self._force_parent_pack_stock_moves()
        return res

    def _create_pack_stock_moves(self):
        production_ids = self.env["mrp.production"]
        for order in self:
            if any(
                [
                    ptype == "consu"
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                moves = order.order_line._create_pack_stock_moves()
                production_ids += moves.mapped("raw_material_production_id")
        if production_ids:
            production_ids.update_move_raw_sequences()
        return True

    def _force_parent_pack_stock_moves(self):
        for order in self:
            if any(
                [
                    ptype == "consu"
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                moves = order.order_line._get_parent_pack_stock_moves()
                moves._action_done()
        return True
