# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import _, models, fields, api
from odoo.exceptions import UserError


class AccountInvoiceUpdate(models.TransientModel):
    _inherit = 'account.invoice.update'

    @api.multi
    def _reopen(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': {
                'default_model': self._name,
            },
        }

    @api.multi
    def remove_lines_with_product_id(self):
        for rec in self:
            lines_with_product = rec.line_ids.filtered(lambda x: x.product_id)
            lines_with_product.unlink()
        return self._reopen()

    @api.multi
    def _get_matching_inv_line(self, move_line):
        try:
            inv_line = super()._get_matching_inv_line(move_line)
        except UserError:
            pass
        inv_line = self.invoice_id._get_matching_inv_line(move_line)
        return inv_line

    @api.multi
    def _get_move_lines(self, move_id):
        move_lines = super()._get_move_lines(move_id)
        # Override default lines and select all
        move_lines = self.env['account.move.line']
        for move_line in move_id.line_ids:
            try:
                self._get_matching_inv_line(move_line)
                # Keep only lines without error
                move_lines += move_line
            except UserError as e:
                pass
        return move_lines

class AccountInvoiceLineUpdate(models.TransientModel):
    _inherit = 'account.invoice.line.update'

    product_id = fields.Many2one(
        'product.product',
        related="invoice_line_id.product_id",
    )
