# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, api, models, fields
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"

    tax_amount = fields.Float(
        string="Taxes",
        digits=dp.get_precision('Account'),
    )
    comments = fields.Char(string="Comments", )

    @api.onchange('tax_amount')
    def onchange_tax_amount(self):
        for expense in self:
            if expense.tax_amount > expense.total_amount:
                raise UserError(_("Invalid tax amount"))

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

    @api.multi
    def _get_account_move_line_values(self):
        # Call super but drop the result as this method is a full copy/paste
        # of `_get_account_move_line_values` from
        # `odoo/addons/hr_expense/models/hr_expense.py` except that we now
        # use the new `tax_amount` field
        super()._get_account_move_line_values()
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.employee_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id
            different_currency = expense.currency_id and expense.currency_id != company_currency

            move_line_values = []
            taxes = expense.tax_ids.with_context(round=True).compute_all(expense.unit_amount, expense.currency_id, expense.quantity, expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.address_home_id.commercial_partner_id.id

            # source move line
            amount = taxes['total_included'] - expense.tax_amount  # taxes['total_excluded']
            amount_currency = False
            if different_currency:
                amount_currency = amount
                amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': amount if amount > 0 else 0,
                'credit': -amount if amount < 0 else 0,
                'amount_currency': amount_currency if different_currency else 0.0,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'currency_id': expense.currency_id.id if different_currency else False,
            }
            move_line_values.append(move_line_src)
            total_amount += -move_line_src['debit'] or move_line_src['credit']
            total_amount_currency += -move_line_src['amount_currency'] if move_line_src['currency_id'] else (-move_line_src['debit'] or move_line_src['credit'])

            # taxes move lines
            for tax in taxes['taxes']:
                amount = expense.tax_amount # tax['amount']
                amount_currency = False
                if different_currency:
                    amount_currency = amount
                    amount = expense.currency_id._convert(amount, company_currency, expense.company_id, account_date)
                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': amount if amount > 0 else 0,
                    'credit': -amount if amount < 0 else 0,
                    'amount_currency': amount_currency if different_currency else 0.0,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_line_id': tax['id'],
                    'expense_id': expense.id,
                    'partner_id': partner_id,
                    'currency_id': expense.currency_id.id if different_currency else False,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= amount
                total_amount_currency -= move_line_tax_values['amount_currency'] or amount
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency if different_currency else 0.0,
                'currency_id': expense.currency_id.id if different_currency else False,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense
    # yapf: enable

    @api.multi
    def action_duplicate(self):
        self.ensure_one()
        self.copy(default={
            'sheet_id': self.sheet_id.id,
        })

    @api.multi
    def action_get_attachment_view(self):
        self.ensure_one()
        if self.attachment_number == 0:
            res = self.action_create_attachment_view()
        else:
            res = super().action_get_attachment_view()
        return res

    @api.multi
    def action_create_attachment_view(self):
        self.ensure_one()
        context = {'default_res_model': self._name, 'default_res_id': self.id}
        domain = [('res_model', '=', self._name), ('res_id', 'in', self.ids)]
        return {
            'name': _('Create attachment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': "ir.attachment",
            'context': context,
            'domain': domain,
        }
