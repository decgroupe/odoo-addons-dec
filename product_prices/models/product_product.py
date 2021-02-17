# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2020

from datetime import datetime

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Override digit field to increase precision and track changes
    standard_price = fields.Float(
        digits=dp.get_precision('Purchase Price'),
        track_visibility='onchange',
    )

    @api.multi
    def write(self, vals):
        if 'list_price' in vals:
            vals['price_write_date'] = fields.Datetime.to_string(
                datetime.now()
            ),
            vals['price_write_uid'] = self.env.user.id
        if 'standard_price' in vals:
            vals['standard_price_write_date'] = fields.Datetime.to_string(
                datetime.now()
            ),
            vals['standard_price_write_uid'] = self.env.user.id
        res = super().write(vals)
        return res

    @api.multi
    def open_price_graph(self):
        self.ensure_one()
        action = self.env.ref('product_prices.act_window_product_price_graph'
                             ).read()[0]
        return action
