# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class HrExpense(models.Model):
    _inherit = "hr.expense"

    manual_tax_amount = fields.Monetary(
        string="Tax amount (manual)",
        currency_field="company_currency_id",
        compute="_compute_manual_tax_amount",
        precompute=True,
        store=True,
        readonly=False,
        help="Manually forced tax amount in company currency",
    )
    automatic_tax_amount = fields.Boolean(
        string="Automatic tax amount",
        compute="_compute_automatic_tax_amount",
        help="Technical field to know if the tax amount was automatically "
        "computed or manually forced",
    )

    @api.depends("product_id")
    def _compute_from_product(self):
        """Always set `product_has_cost` to True to init price unit"""
        res = super()._compute_from_product()
        for expense in self:
            expense.product_has_cost = True
        return res

    def _needs_product_price_computation(self):
        """Disable the price unit computation based on the product cost as we want to
        always have a manual price unit edition."""
        _res = super()._needs_product_price_computation()
        return False

    @api.depends("manual_tax_amount")
    def _compute_tax_amount_currency(self):
        # ensure that all taxes uses the `price_include`
        for expense in self:
            for tax_id in expense.tax_ids:
                if not tax_id.price_include:
                    raise UserError(
                        self.env._(
                            "The tax %(tax)s should be configured with price included",
                            tax=tax_id.display_name,
                        )
                    )
        manual_tax_expenses = self.filtered(lambda exp: not exp.automatic_tax_amount)
        for expense in manual_tax_expenses:
            expense.tax_amount_currency = expense.manual_tax_amount
            expense.untaxed_amount_currency = (
                expense.total_amount_currency - expense.tax_amount_currency
            )
        return super(
            HrExpense, self - manual_tax_expenses
        )._compute_tax_amount_currency()

    @api.depends("price_unit")
    def _compute_tax_amount(self):
        return super()._compute_tax_amount()

    @api.depends("tax_amount")
    def _compute_manual_tax_amount(self):
        for expense in self:
            expense.manual_tax_amount = expense.tax_amount

    @api.depends("tax_amount", "manual_tax_amount")
    def _compute_automatic_tax_amount(self):
        for expense in self:
            expense.automatic_tax_amount = (
                float_compare(
                    expense.tax_amount,
                    expense.manual_tax_amount,
                    precision_rounding=expense.currency_id.rounding,
                )
                == 0
            )

    def action_duplicate(self):
        self.ensure_one()
        if self.state in ["done", "approved"]:
            raise UserError(
                self.env._("You cannot duplicate a posted or approved expense.")
            )
        self.copy(
            default={
                "sheet_id": self.sheet_id.id,
            }
        )

    def action_get_attachment_view(self):
        self.ensure_one()
        if self.nb_attachment == 0:
            res = self.action_create_attachment_view()
        else:
            res = super().action_get_attachment_view()
        return res

    def action_create_attachment_view(self):
        self.ensure_one()
        context = {"default_res_model": self._name, "default_res_id": self.id}
        domain = [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        return {
            "name": self.env._("Create attachment"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_model": "ir.attachment",
            "context": context,
            "domain": domain,
        }
