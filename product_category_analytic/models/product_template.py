# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

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

    @api.multi
    def _get_product_analytic_accounts(self):
        self.ensure_one()
        res = super()._get_product_analytic_accounts()
        if self.categ_id and (not res['income'] or not res['expense']):
            categ_res = self.categ_id._get_category_analytic_accounts()
            if not res['income'] and categ_res['income']:
                res['income'] = categ_res['income']
            if not res['expense'] and categ_res['expense']:
                res['expense'] = categ_res['expense']
        return res

    @api.multi
    @api.depends(
        'income_analytic_account_id', 'expense_analytic_account_id', 'categ_id',
        'categ_id.income_analytic_account_id',
        'categ_id.expense_analytic_account_id'
    )
    def _compute_default_analytic_accounts(self):
        for rec in self:
            accounts = rec._get_product_analytic_accounts()
            rec.income_default_ac_id = accounts['income']
            rec.expense_default_ac_id = accounts['expense']
