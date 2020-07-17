# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_bank_footer = fields.Text(
        'Bank Accounts Footer',
        compute="_compute_bank_footer",
        help="This field is computed automatically based on bank accounts \
defined, having the display on footer checkbox set.",
    )

    @api.multi
    @api.depends('bank_ids')
    def _compute_bank_footer(self):
        for company in self:
            r = []
            for bank in company.bank_ids:
                if bank.footer:
                    n = '{}: {} - {}'.format(
                        bank.bank_name, bank.display_name, bank.bank_bic
                    )
                    r.append(n)
            res = ' | '.join(r)
            company.report_bank_footer = res
