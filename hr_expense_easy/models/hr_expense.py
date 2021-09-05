# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"
