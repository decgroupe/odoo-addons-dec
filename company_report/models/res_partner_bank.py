# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    footer = fields.Boolean(
        string="Display on Reports",
        help="Display this bank account on the footer of printed documents like "
        "invoices and sales orders.",
    )
