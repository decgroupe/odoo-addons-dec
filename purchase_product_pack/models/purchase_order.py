# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Sep 2020


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
