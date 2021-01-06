# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

from odoo import api, fields, models


class RefCategory(models.Model):
    _inherit = 'ref.category'

    income_analytic_account_id = fields.Many2one(
        related='product_category_id.income_analytic_account_id',
        string='Income Analytic Account',
        readonly=False,
    )

    @api.multi
    def action_create_income_analytic_account(self):
        product_analytic_group = self.env.ref(
            'product_reference_analytic.product_analytic_group'
        )
        for category in self.filtered(
            lambda x: not x.income_analytic_account_id
        ):
            category.income_analytic_account_id = self.env[
                'account.analytic.account'].create(
                    {
                        'code': category.code,
                        'name': category.name,
                        'group_id': product_analytic_group.id,
                    }
                )
