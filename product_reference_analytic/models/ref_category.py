# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models


class RefCategory(models.Model):
    _inherit = "ref.category"

    income_analytic_account_id = fields.Many2one(
        related="product_category_id.income_analytic_account_id",
        string="Income Analytic Account",
        readonly=False,
    )

    def action_create_income_analytic_account(self):
        """Create an income analytic account for each category that lacks one."""
        product_analytic_plan = self.env.ref(
            "product_reference_analytic.product_analytic_group"
        )
        for category in self.filtered(lambda x: not x.income_analytic_account_id):
            category.income_analytic_account_id = self.env[
                "account.analytic.account"
            ].create(
                {
                    "code": category.code,
                    "name": category.name,
                    "plan_id": product_analytic_plan.id,
                }
            )

    @api.model_create_multi
    def create(self, vals_list):
        """Create ref.category records and auto-create analytic accounts if enabled."""
        records = super().create(vals_list)
        if self.env.user.company_id.auto_create_reference_category_analytic_account:
            records.action_create_income_analytic_account()
        return records

    def write(self, vals):
        """Update ref.category records and sync analytic account name/code if linked."""
        # sync analytic account name if category name changes
        name = vals.get("name")
        if name:
            for rec in self.filtered("income_analytic_account_id"):
                if rec.income_analytic_account_id.name == self.name:
                    rec.income_analytic_account_id.name = name
        # sync analytic account code if category code changes
        code = vals.get("code")
        if code:
            for rec in self.filtered("income_analytic_account_id"):
                if rec.income_analytic_account_id.code == self.code:
                    rec.income_analytic_account_id.code = code
        res = super().write(vals)
        return res
