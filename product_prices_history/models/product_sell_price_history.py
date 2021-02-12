# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from datetime import datetime

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductSellPriceHistory(models.Model):
    """ Keep track of the ``product.template`` sell prices. """
    _name = 'product.sell.price.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'
    _description = 'Product Sell Price History'

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_default_company_id,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        ondelete='cascade',
        required=True,
    )
    datetime = fields.Datetime(
        'Date',
        default=fields.Datetime.now,
    )
    price = fields.Float(
        'Price',
        digits=dp.get_precision('Product Price'),
    )
