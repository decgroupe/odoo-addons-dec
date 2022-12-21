# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging

from odoo import api, models
from odoo.addons.product_analytic.models.account_move import INV_TYPE_MAP

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _get_product_analytic_account(self, product_id, move_type):
        res = False
        if product_id and move_type:
            ana_accounts = product_id.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[move_type]]
            res = ana_account.id
        return res

    def set_default_analytic_account(self):
        # Copycat from oca product_analytic module:
        # - oca/account-analytic/product_analytic/models/account_invoice.py
        # It is used to re-link with correct analytic account
        for line in self:
            if line.account_analytic_id and not self._context.get(
                'override_existing_account'
            ):
                continue
            line.account_analytic_id = self._get_product_analytic_account(
                line.product_id,
                line.move_type,
            )
