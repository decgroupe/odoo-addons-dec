# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

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
