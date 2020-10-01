# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_quantity_done_greater = fields.Boolean(
        compute='_compute_is_quantity_done_greater',
        store=True,
        compute_sudo=True,
    )

    move_lines_count = fields.Integer(
        compute='_compute_move_lines_count',
        store=True,
        compute_sudo=True,
    )

    @api.multi
    @api.depends('product_uom_qty', 'quantity_done')
    def _compute_is_quantity_done_greater(self):
        for move in self:
            move.is_quantity_done_greater = (
                move.quantity_done > move.product_uom_qty
            )

    @api.depends('move_line_ids')
    def _compute_move_lines_count(self):
        for move in self:
            move.move_lines_count = len(move.move_line_ids)
