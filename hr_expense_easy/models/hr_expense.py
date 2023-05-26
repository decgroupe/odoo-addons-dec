# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    tax_amount = fields.Float(
        string="Taxes",
        digits="Account",
    )
    comments = fields.Char(
        string="Comments",
    )

    @api.onchange("tax_amount")
    def onchange_tax_amount(self):
        for expense in self:
            if expense.tax_amount > expense.total_amount:
                raise UserError(_("Invalid tax amount"))

    @api.depends("tax_amount")
    def _compute_amount(self):
        # Do not override the original `_compute_amount` result.
        # Instead, we ensure that all taxes uses the `price_include`
        for expense in self:
            for tax_id in expense.tax_ids:
                if not tax_id.price_include:
                    raise UserError(
                        _("The tax %s should be configured with price included")
                        % (tax_id.display_name),
                        self,
                    )
        super()._compute_amount()

    # yapf: disable
    @api.onchange('quantity', 'unit_amount', 'tax_ids', 'currency_id')
    def rebuild_tax_amount(self):
        # Use the same code from `_compute_amount` in
        # `odoo/addons/hr_expense/models/hr_expense.py` but store the tax
        # amount in its own field, allowing employee to edit it.
        for expense in self:
            expense.untaxed_amount = expense.unit_amount * expense.quantity
            taxes = expense.tax_ids.compute_all(
                expense.unit_amount, expense.currency_id, expense.quantity,
                expense.product_id, expense.employee_id.user_id.partner_id
            )
            expense.tax_amount = taxes.get('total_included') - taxes.get('total_excluded')

    def _get_account_move_line_values(self):
        # Call super but drop the result as this method is a full copy/paste
        # of `_get_account_move_line_values` from
        # `odoo/addons/hr_expense/models/hr_expense.py` except that we now
        # use the new `tax_amount` field so:
        # - Calls to taxes['total_excluded'] are replaced with taxes['total_included'] - expense.tax_amount
        # - Calls to tax['amount'] are replaced with expense.tax_amount
        move_line_values_by_expense = super()._get_account_move_line_values()
        # Reset values
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id
            total_excluded = taxes['total_included'] - expense.tax_amount

            # source move line
            balance = expense.currency_id._convert(total_excluded, company_currency, expense.company_id, account_date)
            amount_currency = total_excluded
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(expense.tax_amount, company_currency, expense.company_id, account_date)
                amount_currency = expense.tax_amount # tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense
    # yapf: enable

    def action_duplicate(self):
        self.ensure_one()
        if self.state in ["done", "approved"]:
            raise UserError(_("You cannot duplicate a posted or approved expense."))
        self.copy(
            default={
                "sheet_id": self.sheet_id.id,
            }
        )

    def action_get_attachment_view(self):
        self.ensure_one()
        if self.attachment_number == 0:
            res = self.action_create_attachment_view()
        else:
            res = super().action_get_attachment_view()
        return res

    def action_create_attachment_view(self):
        self.ensure_one()
        context = {"default_res_model": self._name, "default_res_id": self.id}
        domain = [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        return {
            "name": _("Create attachment"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "target": "new",
            "res_model": "ir.attachment",
            "context": context,
            "domain": domain,
        }
