# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.one
    def _set_valuation_type(self):
        # Do not set property_valuation otherwise category valuation property
        # will never be taken into account
        pass
