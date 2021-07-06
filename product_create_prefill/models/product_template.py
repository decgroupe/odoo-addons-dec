# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2021

import importlib

from odoo import api, models

from . import parser


class Product(models.Model):
    _inherit = 'product.template'

    @api.model
    def prefill(self, url):
        importlib.reload(parser)
        res = parser.parse_html_product_page(url)
        return res
