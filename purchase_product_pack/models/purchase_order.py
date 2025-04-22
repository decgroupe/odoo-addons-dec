# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import _, api, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def copy(self, default=None):
        purchase_copy = super().copy(default)
        # we unlink pack lines that should not be copied
        # FIXME: this is not a good idea to do this: instead we should let the ORM copy
        # the lines with same values an disabling the automatic expansion of the pack,
        # this future fix should also be done in in `sale_product_pack` module
        pack_copied_lines = purchase_copy.order_line.filtered(
            lambda l: l.pack_parent_line_id.order_id == self
        )
        pack_copied_lines.with_context(bypass_check_pack_line=True).unlink()
        return purchase_copy

    @api.onchange("order_line")
    def check_pack_line_unlink(self):
        """At least on embeded tree editable view odoo returns a recordset on
        _origin.order_line only when lines are unlinked and this is exactly
        what we need
        """
        origin_line_ids = self._origin.order_line.ids
        line_ids = self.order_line.ids
        removed_line_ids = list(set(origin_line_ids) - set(line_ids))
        removed_line = self.env["purchase.order.line"].browse(removed_line_ids)
        removed_line._check_pack_line_unlink()

    def write(self, vals):
        return super(PurchaseOrder, self).write(vals)

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
                    ptype in ["product", "consu"]
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
                    ptype in ["product", "consu"]
                    for ptype in order.order_line.mapped("product_id.type")
                ]
            ):
                moves = order.order_line._get_parent_pack_stock_moves()
                moves.action_auto_operation_fill()
                moves._action_done()
        return True
