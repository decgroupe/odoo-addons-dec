# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    finished_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_finished_picking",
        string="Pickings associated with this manufacturing order output",
    )
    finished_picking_names = fields.Text(
        compute="_compute_finished_picking",
        string="Pickings names associated with this manufacturing order output",
    )
    finished_picking_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_finished_picking",
        string="Moves on pickings associated with this manufacturing order output",
    )

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, vals in zip(record_ids, vals_list, strict=True):
            # Update finished moves or they will be named « New »
            if vals.get("move_finished_ids"):
                rec.move_finished_ids.write({"name": rec.name})
            # Update raw moves or they will be named « New »
            if vals.get("move_raw_ids"):
                rec.move_raw_ids.write({"name": rec.name})
            rec._update_raw_move_conv_dest_ids(vals)
        return record_ids

    def write(self, vals):
        res = super().write(vals)
        self._update_raw_move_conv_dest_ids(vals)
        return res

    def _update_raw_move_conv_dest_ids(self, vals=None):
        """Link move destination to production moves to-do to improve traceability with
        some custom tools.
        """
        if not vals or vals.get("move_finished_ids") or vals.get("move_raw_ids"):
            for rec in self:
                if rec.move_finished_ids.ids and rec.move_raw_ids.ids:
                    rec.move_raw_ids.write(
                        {"move_conv_dest_ids": [(6, 0, self.move_finished_ids.ids)]}
                    )

    def _compute_finished_picking(self):
        def get_pickings(move):
            # We need to return moves and pickings so we are creating
            # two empty recordset
            move_ids = self.env["stock.move"]
            picking_ids = self.env["stock.picking"]
            if move.picking_id:
                move_ids = move_ids | move
                picking_ids = picking_ids | move.picking_id
            # Make a recursive call while destination moves exists
            for dest_move in move.move_dest_ids:
                sub_move_ids, sub_picking_ids = get_pickings(dest_move)
                move_ids = move_ids | sub_move_ids
                picking_ids = picking_ids | sub_picking_ids
            # Return as a tuple
            return move_ids, picking_ids

        for production in self:
            all_move_ids = self.env["stock.move"]
            all_picking_ids = self.env["stock.picking"]
            for move in production.move_finished_ids:
                move_ids, picking_ids = get_pickings(move)
                all_move_ids = all_move_ids | move_ids
                all_picking_ids = all_picking_ids | picking_ids

            production.finished_picking_names = "\n".join(
                o.name for o in all_picking_ids
            )
            production.finished_picking_ids = all_picking_ids.ids
            production.finished_picking_move_ids = all_move_ids.ids
