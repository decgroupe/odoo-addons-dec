# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import _, api, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def copy(self, default=None):
        purchase_copy = super().copy(default)
        # we unlink pack lines that should not be copied
        pack_copied_lines = purchase_copy.order_line.filtered(
            lambda l: l.pack_parent_line_id.order_id == self
        )
        pack_copied_lines.unlink()
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
        if "order_line" in vals:
            disable_pack_line_unlink = False
            # find all lines that will be deleted using the command "2:UNLINK"
            to_delete_ids = [e[1] for e in vals["order_line"] if e[0] == 2]
            # search all existing pack lines that are children of these deleted lines
            subpacks_to_delete_ids = (
                self.env["purchase.order.line"]
                .search(
                    [("id", "child_of", to_delete_ids), ("id", "not in", to_delete_ids)]
                )
                .ids
            )
            # hook the current write data and replace any existing command with
            # "2:UNLINK"
            if subpacks_to_delete_ids:
                # manually convert tuples to lists to keep compatibilty with odoo Form
                # test
                vals["order_line"] = [list(x) for x in vals["order_line"]]
                for cmd in vals["order_line"]:
                    if cmd[1] in subpacks_to_delete_ids:
                        if cmd[0] != 2:
                            cmd[0] = 2
                            disable_pack_line_unlink = True
                        subpacks_to_delete_ids.remove(cmd[1])
                for to_delete_id in subpacks_to_delete_ids:
                    vals["order_line"].append([2, to_delete_id, False])
            # add a context variable to disable the automatic deletion of the pack lines
            if disable_pack_line_unlink:
                self = self.with_context(disable_pack_line_unlink=True)
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
