# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import Command, models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    _parent_name = "pack_parent_line_id"

    def unlink(self):
        """Remove previously the pack children lines for avoiding issues in
        the cache.
        """
        if not self.env.context.get("bypass_check_pack_line"):
            self._check_pack_line_unlink()
        children = self.mapped("pack_child_line_ids")
        if children:
            children._pre_unlink()
            children.with_context(bypass_check_pack_line=True).unlink()
        return super().unlink()

    def _pre_unlink(self):
        """Delete existing moves before calling unlink (because some modules
        like 'purchase_stock_cancel' could already have unset the link with
        'move_dest_ids').
        """
        for record in self:
            if record.pack_parent_line_id and record.move_dest_ids:
                record.move_dest_ids._action_cancel()
                record.move_dest_ids.unlink()

    def _check_pack_line_unlink(self):
        undeletable_lines = self.filtered(
            lambda x: x.pack_parent_line_id
            and not x.pack_parent_line_id.product_id.pack_modifiable
        )
        if undeletable_lines:
            po_lines = "\n".join(undeletable_lines.mapped("name"))
            raise UserError(
                self.env._(
                    "You cannot delete these lines because they are part of a pack in"
                    " this purchase order:\n %(po_lines)s\n\n"
                    "To remove these lines, you need to delete the pack itself",
                    po_lines=po_lines,
                )
            )

    def _get_pack_line_move_data(self, move):
        self.ensure_one()
        res = {
            # Set from purchase line
            "product_id": self.product_id.id,
            "product_uom": self.product_id.uom_id.id,
            "product_uom_qty": self.product_uom_qty,
            "name": self.name,
            "created_purchase_line_ids": [Command.link(self.id)],
            # Copy parent move data
            "company_id": move.company_id.id,
            "picking_id": move.picking_id.id,
            "picking_type_id": move.picking_type_id.id,
            "reference": move.reference,
            "date": move.date,
            "date_deadline": move.date_deadline,
            "propagate_cancel": move.propagate_cancel,
            "partner_id": move.partner_id.id,
            "procure_method": move.procure_method,
            "location_id": move.location_id.id,
            "location_dest_id": move.location_dest_id.id,
            "origin": move.origin,
            "group_id": move.group_id.id,
            "warehouse_id": move.warehouse_id.id,
            "raw_material_production_id": move.raw_material_production_id.id,
            "auto_validate": move.auto_validate,
            "move_dest_ids": [(6, 0, move.move_dest_ids.ids)],
            "state": move.state,
            "sequence": move.sequence,
            # Set as pack line, will auto-set pack_child_move_ids on its parent
            "pack_parent_move_id": move.id,
        }
        return res

    def _create_pack_stock_moves(self):
        moves = self.env["stock.move"]
        for line in self:
            if line.pack_parent_line_id and line.pack_parent_line_id.move_dest_ids:
                parent_move = line.pack_parent_line_id.move_dest_ids[0]
                data = line._get_pack_line_move_data(parent_move)
                child_move = self.env["stock.move"].create(data)
                moves += child_move
        return moves

    def _get_parent_pack_stock_moves(self):
        moves = self.env["stock.move"]
        for line in self:
            # Set parent pack move done since there is no
            # physical pack item to receive
            if line.pack_child_line_ids:
                moves += line.move_dest_ids
                moves += line.move_ids
        return moves
