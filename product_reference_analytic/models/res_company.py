# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    auto_create_reference_category_analytic_account = fields.Boolean(
        default=True,
    )
