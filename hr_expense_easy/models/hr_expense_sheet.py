# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

from odoo import api, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"