# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    action_auto_operation_fill_visible = fields.Boolean(
        "Show button to auto fill operations",
        compute='_compute_action_auto_operation_fill_visible',
        readonly=True,
    )

    def _compute_action_auto_operation_fill_visible(self):
        for move in self:
            visible = move.quantity_done < move.reserved_availability
            move.action_auto_operation_fill_visible = visible

    # Copy logic from :
    # ./odoo-addons/oca/stock-logistics-workflow/stock_move_line_auto_fill/models/stock_picking.py
    def action_auto_operation_fill(self):
        for move in self:
            operations = move.mapped('move_line_ids')
            operations_to_auto_fill = operations.filtered(
                lambda op: (
                    op.product_id and not op.qty_done and (
                        not op.lots_visible or not op.picking_id.picking_type_id
                        .avoid_lot_assignment
                    )
                )
            )
            for op in operations_to_auto_fill:
                op.qty_done = op.product_uom_qty
