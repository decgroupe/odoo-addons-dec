# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
