# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountInvoiceUpdate(models.TransientModel):
    _inherit = "account.move.update"

    def _reopen(self):
        """Return the action to reopen this wizard in a new dialog."""
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }

    def remove_lines_with_product_id(self):
        """Remove wizard lines that have a product assigned, then reopen."""
        for rec in self:
            lines_with_product = rec.line_ids.filtered(lambda x: x.product_id)
            lines_with_product.unlink()
        return self._reopen()

    def _get_matching_inv_line(self, move_line):
        """Return the invoice line matching the given move line."""
        try:
            super()._get_matching_inv_line(move_line)
        except (UserError, AttributeError) as e:
            _logger.debug("Parent _get_matching_inv_line not available: %s", e)
        inv_line = self.invoice_id._get_matching_inv_line(move_line)
        return inv_line

    def _get_move_lines(self, move_id):
        """Return all move lines instead of the default filtered set."""
        # override default lines and select all
        return move_id.line_ids


class AccountInvoiceLineUpdate(models.TransientModel):
    _inherit = "account.move.line.update"

    product_id = fields.Many2one(
        comodel_name="product.product",
        related="invoice_line_id.product_id",
    )
