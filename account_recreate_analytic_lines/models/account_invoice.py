# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import api, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_matching_inv_line(self, move_line):
        self.ensure_one()
        move_line.ensure_one()
        """ Find matching invoice line by product """
        # TODO make it accept more case as lines won't
        # be grouped unless journal.group_invoice_line is True
        inv_line = self.invoice_line_ids.filtered(
            lambda x: x.product_id == move_line.product_id
        )
        if len(inv_line) != 1:
            raise UserError(
                "Cannot match a single invoice line to move line %s" %
                move_line.name
            )
        return inv_line

    @api.multi
    def action_set_default_analytic_account(self):
        for rec in self:
            rec.invoice_line_ids.set_default_analytic_account()
            # If invoice state is already open/paid then the account.move
            # already exists and will not be updated with current invoice lines
            # So we need to manually set analytic_account_id
            if rec.move_id:
                for ml in rec.move_id.line_ids.filtered(
                    # we are only interested in invoice lines, not tax lines
                    lambda x: bool(x.product_id)
                ):
                    if ml.credit == 0.0:
                        continue
                    ml.analytic_line_ids.unlink()
                    analytic_account_id = False
                    try:
                        inv_line = rec._get_matching_inv_line(ml)
                        analytic_account_id = inv_line.account_analytic_id
                    except UserError:
                        # If we are not able to find a match, then fallback
                        # to raw way by directly finding analytic account from
                        # account.move product_id
                        analytic_account_id = self.env[
                            'account.invoice.line'
                        ]._get_product_analytic_account(
                            ml.product_id, rec.type
                        )
                    ml.analytic_account_id = analytic_account_id
                    ml.create_analytic_lines()
