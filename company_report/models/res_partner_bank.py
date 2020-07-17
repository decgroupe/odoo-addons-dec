# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    footer = fields.Boolean(
        "Display on Reports",
        help="Display this bank account on the footer of printed documents like invoices and sales orders.",
    )
