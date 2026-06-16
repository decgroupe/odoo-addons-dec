# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging

from odoo import api, models

from odoo.addons.product_analytic_legacy.models.account_move import INV_TYPE_MAP

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _get_product_analytic_distribution(self, product_id, move_type):
        """Return analytic distribution dict for a product and move type."""
        res = False
        if product_id and move_type:
            ana_accounts = product_id.product_tmpl_id._get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[move_type]]
            res = {ana_account.id: 100} if ana_account else False
        return res

    def set_default_analytic_account(self):
        """Set default analytic distribution on lines based on product and move type."""
        # copycat from oca product_analytic module:
        # - oca/account-analytic/product_analytic/models/account_invoice.py
        # it is used to re-link with correct analytic account
        for line in self:
            if line.analytic_distribution and not self._context.get(
                "override_existing_account"
            ):
                continue
            line.analytic_distribution = self._get_product_analytic_distribution(
                line.product_id,
                line.move_id.move_type,
            )
