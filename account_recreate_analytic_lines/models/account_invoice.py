# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.progressbar import progressbar as pb

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_matching_inv_line(self, move_line):
        self.ensure_one()
        move_line.ensure_one()
        inv_line = self.env["account.move.line"]
        if move_line.product_id:
            """Find matching invoice line by product"""
            # TODO make it accept more case as lines won't
            # be grouped unless journal.group_invoice_line is True
            inv_line = self.invoice_line_ids.filtered(
                lambda x: x.product_id == move_line.product_id
            )
        elif move_line.name:
            for line in self.invoice_line_ids.filtered("name").filtered(
                lambda x: x.name.startswith(move_line.name)
            ):
                if (
                    line.invoice_line_tax_ids.ids == move_line.tax_ids.ids
                    and line.price_subtotal == move_line.credit
                ):
                    inv_line += line
        if len(inv_line) != 1:
            raise UserError(
                _("Cannot match a single invoice line to move line %s (%d match)")
                % (move_line.name, len(inv_line))
            )
        return inv_line

    def action_set_default_analytic_account(self):
        for rec in pb(self):
            rec._set_default_analytic_account()

    def _set_default_analytic_account(self):
        self.ensure_one()
        inv = self
        inv.invoice_line_ids.set_default_analytic_account()
        # If invoice state is already open/paid then the account.move
        # already exists and will not be updated with current invoice lines
        # So we need to manually set analytic_account_id
        for ml in inv.line_ids.filtered(
                # we are only interested in invoice lines, not tax lines
                lambda rec: bool(rec.product_id)
        ):
            if ml.credit == 0.0:
                continue
            if (
                not self._context.get("override_existing_account")
                and ml.analytic_line_ids
            ):
                continue
            ml.analytic_line_ids.unlink()
            analytic_account_id = False
            try:
                inv_line = self._get_matching_inv_line(ml)
                analytic_account_id = inv_line.analytic_account_id
            except UserError as e:
                _logger.warning(e.name or e.value)
                # If we are not able to find a match, then fallback
                # to raw way by directly finding analytic account from
                # account.move product_id
                analytic_account_id = self.env[
                    "account.move.line"
                ]._get_product_analytic_account(ml.product_id, inv.move_type)
            if analytic_account_id:
                _logger.info("Recreate analytic lines for %s", ml.name)
                ml.analytic_account_id = analytic_account_id
                ml.create_analytic_lines()
