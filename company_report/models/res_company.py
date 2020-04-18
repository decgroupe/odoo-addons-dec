# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

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
                    r.append(bank.name_get()[0][1])
            res = ' | '.join(r)
            company.report_bank_footer = res
