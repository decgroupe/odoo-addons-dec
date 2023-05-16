# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountInvoiceUpdate(models.TransientModel):
    _inherit = "account.move.update"

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }

    def remove_lines_with_product_id(self):
        for rec in self:
            lines_with_product = rec.line_ids.filtered(lambda x: x.product_id)
            lines_with_product.unlink()
        return self._reopen()

    def _get_matching_inv_line(self, move_line):
        try:
            inv_line = super()._get_matching_inv_line(move_line)
        except UserError:
            pass
        inv_line = self.invoice_id._get_matching_inv_line(move_line)
        return inv_line

    def _get_move_lines(self, move_id):
        move_lines = super()._get_move_lines(move_id)
        # Override default lines and select all
        return move_id.line_ids


class AccountInvoiceLineUpdate(models.TransientModel):
    _inherit = "account.move.line.update"

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="invoice_line_id.product_id",
    )
