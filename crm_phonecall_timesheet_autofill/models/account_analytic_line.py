# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def get_autofill_fields(self):
        res = super().get_autofill_fields()
        return res + ['phonecall_id']
