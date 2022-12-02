# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    income_default_ac_id = fields.Many2one(
        'account.analytic.account',
        string='Income Default Analytic Account',
        compute='_compute_default_analytic_accounts',
    )
    expense_default_ac_id = fields.Many2one(
        'account.analytic.account',
        string='Expense Default Analytic Account',
        compute='_compute_default_analytic_accounts',
    )

    def _get_category_analytic_accounts(self):
        self.ensure_one()
        res = {
            'income': self.income_analytic_account_id,
            'expense': self.expense_analytic_account_id
        }
        if self.parent_id and (not res['income'] or not res['expense']):
            parent_res = self.parent_id._get_category_analytic_accounts()
            if not res['income'] and parent_res['income']:
                res['income'] = parent_res['income']
            if not res['expense'] and parent_res['expense']:
                res['expense'] = parent_res['expense']
        return res

    @api.depends(
        'income_analytic_account_id', 'expense_analytic_account_id',
        'parent_id', 'parent_id.income_analytic_account_id',
        'parent_id.expense_analytic_account_id'
    )
    def _compute_default_analytic_accounts(self):
        for rec in self:
            accounts = rec._get_category_analytic_accounts()
            rec.income_default_ac_id = accounts['income']
            rec.expense_default_ac_id = accounts['expense']
