# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    pack_parent_move_id = fields.Many2one(
        'stock.move',
        'Pack',
        help='The pack that contains this product.',
        ondelete="cascade",
    )
    pack_child_move_ids = fields.One2many(
        'stock.move', 'pack_parent_move_id', 'Lines in pack'
    )
    pack_level = fields.Integer(compute='_compute_pack_level')

    def _compute_pack_level(self):
        for move in self:
            move.pack_level = 0
            if move.pack_parent_move_id:
                move.pack_level = move.pack_parent_move_id.pack_level + 1

    def _update_sequence(self, sequence=0, updated_ids=None):
        if updated_ids is None:
            updated_ids = []
        if not sequence:
            sequence = 1

        for move in self:
            if not move.id in updated_ids:
                # If the move is a part of pack but its parent sequence
                # has not been updated yet, then ignore it. It will be
                # updated by its parent when procvessing its
                # pack_child_move_ids
                if move.pack_parent_move_id and move.pack_parent_move_id.id not in updated_ids:
                    continue
                updated_ids.append(move.id)
                move.sequence = sequence
                sequence += 1
                # Update pack line sequences recursively
                if move.pack_child_move_ids:
                    sequence = move.pack_child_move_ids._update_sequence(
                        sequence, updated_ids
                    )
        return sequence
