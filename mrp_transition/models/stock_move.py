# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    compare_quantity_done = fields.Integer(
        compute='_compute_compare_quantity_done',
        store=True,
        compute_sudo=True,
        help="Compare quantity_done with product_uom_qty :"
        "\n - Return 1 if quantity_done > product_uom_qty"
        "\n - Return 0 if quantity_done = product_uom_qty"
        "\n - Return -1 if quantity_done < product_uom_qty"
    )

    move_lines_count = fields.Integer(
        compute='_compute_move_lines_count',
        store=True,
        compute_sudo=True,
    )

    @api.multi
    @api.depends('product_uom_qty', 'quantity_done')
    def _compute_compare_quantity_done(self):
        for move in self:
            rounding = move.product_id.uom_id.rounding
            move.compare_quantity_done = float_compare(
                move.quantity_done,
                move.product_uom_qty,
                precision_rounding=rounding,
            )

    @api.depends('move_line_ids')
    def _compute_move_lines_count(self):
        for move in self:
            move.move_lines_count = len(move.move_line_ids)
