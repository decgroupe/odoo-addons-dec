# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2020

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Override digit field to increase precision
    standard_price = fields.Float(digits=dp.get_precision('Purchase Price'), )

    @api.multi
    def open_price_graph(self):
        self.ensure_one()
        action = self.env.ref('product_prices.act_window_product_price_graph'
                             ).read()[0]
        return action
