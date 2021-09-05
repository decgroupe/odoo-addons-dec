# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models, api, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def copy(self, default=None):
        purchase_copy = super().copy(default)
        # we unlink pack lines that should not be copied
        pack_copied_lines = purchase_copy.order_line.filtered(
            lambda l: l.pack_parent_line_id.order_id == self
        )
        pack_copied_lines.unlink()
        return purchase_copy

    @api.onchange('order_line')
    def check_pack_line_unlink(self):
        """At least on embeded tree editable view odoo returns a recordset on
        _origin.order_line only when lines are unlinked and this is exactly
        what we need
        """
        if self._origin.order_line.filtered(
            lambda x: x.pack_parent_line_id and not x.pack_parent_line_id.
            product_id.pack_modifiable
        ):
            raise UserError(
                _(
                    'You can not delete this line because is part of a pack in'
                    ' this purchase order. In order to delete this line you need'
                    ' to delete the pack itself'
                )
            )

    @api.multi
    def _create_picking(self):
        self._create_pack_stock_moves()
        res = super()._create_picking()
        self._force_parent_pack_stock_moves()
        return res

    @api.multi
    def _create_pack_stock_moves(self):
        production_ids = self.env['mrp.production']
        for order in self:
            if any(
                [
                    ptype in ['product', 'consu']
                    for ptype in order.order_line.mapped('product_id.type')
                ]
            ):
                moves = order.order_line._create_pack_stock_moves()
                production_ids += moves.mapped('raw_material_production_id')
        if production_ids:
            production_ids.update_move_raw_sequences()
        return True

    @api.multi
    def _force_parent_pack_stock_moves(self):
        for order in self:
            if any(
                [
                    ptype in ['product', 'consu']
                    for ptype in order.order_line.mapped('product_id.type')
                ]
            ):
                moves = order.order_line._get_parent_pack_stock_moves()
                moves.action_auto_operation_fill()
                moves._action_done()
        return True
