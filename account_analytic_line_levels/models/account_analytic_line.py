# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import progressbar

from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    account_primary_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account (Primary)',
        compute='_compute_analytic_account_level',
        store=True
    )
    account_secondary_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account (Secondary)',
        compute='_compute_analytic_account_level',
        store=True
    )
    account_tertiary_id = fields.Many2one(
        'account.analytic.account',
        string='Analytic Account (Tertiary)',
        compute='_compute_analytic_account_level',
        store=True
    )

    @api.multi
    @api.depends('account_id', 'account_id.parent_id')
    def _compute_analytic_account_level(self):
        for rec in self:
            accounts = []
            account_id = rec.account_id
            while account_id:
                accounts.insert(0, account_id)
                account_id = account_id.parent_id
            # Fill missing value with False to unset them
            while(len(accounts) < 3):
                accounts.append(False)
            rec.account_primary_id = accounts[0]
            rec.account_secondary_id = accounts[1]
            rec.account_tertiary_id = accounts[2]
