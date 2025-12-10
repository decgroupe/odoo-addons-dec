# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    report_bank_footer = fields.Text(
        string="Bank Accounts Footer",
        compute="_compute_bank_footer",
        help="This field is computed automatically based on bank accounts "
        "defined, having the display on footer checkbox set.",
    )

    @api.depends(
        "bank_ids",
        "bank_ids.footer",
        "bank_ids.bank_name",
        "bank_ids.acc_number",
        "bank_ids.bank_bic",
    )
    def _compute_bank_footer(self):
        for company in self:
            r = []
            for partner_bank in company.bank_ids:
                if partner_bank.footer:
                    if partner_bank.bank_id:
                        n = (
                            f"{partner_bank.bank_name}: "
                            f"{partner_bank.acc_number} - {partner_bank.bank_bic}"
                        )
                    else:
                        n = partner_bank.display_name
                    r.append(n)
            res = " | ".join(r)
            company.report_bank_footer = res
