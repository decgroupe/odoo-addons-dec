# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, May 2020

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class Product(models.Model):
    _inherit = 'product.product'

    default_purchase_price = fields.Monetary(
        compute='_compute_default_purchase_price',
        string='Purchase price',
        digits=dp.get_precision('Purchase Price'),
        help="Purchase price based on default seller pricelist",
    )
    default_sell_price = fields.Monetary(
        compute='_compute_default_sell_price',
        string='Sell price',
        digits=dp.get_precision('Product Price'),
        help="Sell price based on default sell pricelist",
    )
    pricelist_bypass = fields.Boolean(
        'By-pass',
        help=
        "A bypass action will create a pricelist item to overwrite pricelist computation",
    )
    market_place = fields.Boolean(
        'Market place',
        help="Tip to know if the product must be displayed on the market place",
    )
    price_write_date = fields.Datetime('Price write date')
    price_write_uid = fields.Many2one(
        'res.users',
        'Price last editor',
    )
    standard_price_write_date = fields.Datetime('Standard price write date')
    standard_price_write_uid = fields.Many2one(
        'res.users',
        'Standard price last editor',
    )

    @api.depends('company_id')
    def _compute_default_purchase_price(self):
        for product in self:
            price = 0
            product.default_purchase_price = price

    @api.depends('company_id')
    def _compute_default_sell_price(self):
        for product in self:
            price = 0
            product.default_sell_price = price
