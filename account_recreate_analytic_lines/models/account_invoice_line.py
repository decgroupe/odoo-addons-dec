# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging

from odoo import api, models
from odoo.addons.product_analytic.models.account_invoice import INV_TYPE_MAP

_logger = logging.getLogger(__name__)

class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.model
    def _get_product_analytic_account(self, product_id, invoice_type):
        res = False
        if product_id and invoice_type:
            ana_accounts = product_id.product_tmpl_id.\
                _get_product_analytic_accounts()
            ana_account = ana_accounts[INV_TYPE_MAP[invoice_type]]
            res = ana_account.id
        return res

    @api.multi
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
                line.invoice_id.type,
            )
