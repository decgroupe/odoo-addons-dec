# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from datetime import datetime

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductPricesHistory(models.Model):
    """ Keep track of the ``product.template`` purchase and sell prices. """
    _name = 'product.prices.history'
    _rec_name = 'datetime'
    _order = 'datetime desc'
    _description = 'Product Prices History'

    def _get_default_company_id(self):
        return self._context.get('force_company', self.env.user.company_id.id)

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=_get_default_company_id,
        required=True,
    )
    company_currency_id = fields.Many2one(
        related='company_id.currency_id',
        readonly=True,
        compute_sudo=True,
        string='Company Currency',
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
    type = fields.Selection(
        [
            ('purchase', 'Purchase'),
            ('sell', 'Sell'),
        ],
        required=True,
    )
    purchase_price = fields.Float(
        'Purchase Price',
        digits=dp.get_precision('Purchase Price'),
    )
    sell_price = fields.Float(
        'Sell Price',
        digits=dp.get_precision('Product Price'),
    )

    def get_price(self, price_type):
        if price_type == 'purchase':
            assert(self.type == price_type)
            return self.purchase_price
        if price_type == 'sell':
            assert(self.type == price_type)
            return self.sell_price
