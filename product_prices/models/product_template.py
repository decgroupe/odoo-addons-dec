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

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
    pricelist_bypass_item = fields.Many2one(
        'product.pricelist.item',
        'Pricelist item',
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

    @api.depends('seller_id', 'standard_price')
    def _compute_default_purchase_price(self):
        for product in self:
            if product.seller_id:
                pricelist = product.seller_id.property_product_pricelist_purchase
                if pricelist:
                    price = pricelist.with_context(uom=product.uom_po_id.id
                                                  ).price_get(
                                                      product.id,
                                                      1.0,
                                                      product.seller_id.id,
                                                  )[pricelist.id]
            else:
                price = product.standard_price

            product.default_purchase_price = price

    @api.depends('company_id', 'seller_id', 'list_price')
    def _compute_default_sell_price(self):
        for product in self:
            if product.seller_id \
                and product.company_id and product.company_id.partner_id:
                pricelist = product.company_id.partner_id.property_product_pricelist
                if pricelist:
                    price = pricelist.with_context(uom=product.uom_id.id
                                                  ).price_get(
                                                      product.id,
                                                      1.0,
                                                      product.seller_id.id,
                                                  )[pricelist.id]
            else:
                price = product.list_price

            product.default_sell_price = price

    @api.multi
    def update_bypass(self, state):
        Pricelist = self.env['product.pricelist']
        PricelistItem = self.env['product.pricelist.item']
        for product in self:
            pricelists = Pricelist.search([('type', '=', 'sale')])
            pricelist_items = PricelistItem.search(
                [
                    ('pricelist_id', 'in', pricelists.ids),
                    '|',
                    ('product_tmpl_id', '=', product.id),
                    ('product_id', '=', product.id),
                ]
            )

            if state:
                if not pricelist_items:
                    data = {
                        'pricelist_id': pricelists.ids[0],
                        'product_tmpl_id': product.id,
                        'product_id': product.id,
                        'compute_price': 'formula',
                        'applied_on': '1_product',
                        'base': 'list_price',
                        'company_id': product.company_id.id,
                    }
                    product.pricelist_bypass_item = PricelistItem.create(data)
            else:
                if len(pricelist_items) > 1:
                    raise UserError(
                        _(
                            'Too many pricelist items for this product!, only \
one sale pricelist item must exist for this product to disable by-pass \
functionality'
                        )
                    )
                elif pricelist_items:
                    pricelist_items.unlink()

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
        if 'pricelist_bypass' in vals:
            self.update_bypass(state=vals['pricelist_bypass'])
        res = super().write(vals)
        return res
