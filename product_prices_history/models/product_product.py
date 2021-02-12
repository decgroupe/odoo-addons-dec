# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import logging
from progressbar import progressbar

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def scheduler_update_default_prices(self):
        # TODO: First search for the latest entry in history to get the most
        # recent date, then filter stock move by this date to reduce the
        # task charge
        # TODO: Also call update prices when a stock move is done (like it
        # is currently done for stock `real_time` valuation)
        move_ids = self.env['stock.move'].search([])
        move_group = self.env['stock.move'].read_group(
            [('id', 'in', move_ids.ids)], ['product_id'], ['product_id'],
            lazy=False
        )
        product_ids = [x['product_id'][0] for x in move_group]
        self.search(
            [
                ('id', 'in', product_ids),
                ('type', '=', 'product'),
                ('purchase_ok', '=', True),
            ]
        ).update_default_purchase_price()
        self.search(
            [
                ('id', 'in', product_ids),
                ('type', '=', 'product'),
                ('sale_ok', '=', True),
            ]
        ).update_default_sell_price()

    @api.multi
    def update_default_prices(self):
        self.update_default_purchase_price()
        self.update_default_sell_price()

    @api.multi
    def update_default_purchase_price(self):
        precision = self.env['decimal.precision'].precision_get(
            'Purchase Price'
        )
        for rec in progressbar(self.with_context(prefetch_fields=False)):
            rec._update_default_price(
                rec.default_purchase_price,
                precision,
                self.env['product.purchase.price.history'],
            )

    @api.multi
    def update_default_sell_price(self):
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for rec in progressbar(self.with_context(prefetch_fields=False)):
            rec._update_default_price(
                rec.default_sell_price,
                precision,
                self.env['product.sell.price.history'],
            )

    def _update_default_price(self, price, precision, PriceHistory):
        ''' Store default sell and purchase prices which can be computed
            using different pricelist rules
        '''
        print(
            'Updating price history of %s (%d)' % (self.display_name, self.id)
        )
        company_id = self._context.get(
            'force_company', self.env.user.company_id.id
        )

        history = PriceHistory.search(
            [
                ('company_id', '=', company_id), ('product_id', 'in', self.ids),
                ('datetime', '<=', fields.Datetime.now())
            ],
            order='datetime desc, id desc',
            limit=1
        )

        if float_compare(price, history.price, precision_digits=precision) != 0:
            history = PriceHistory.create(
                {
                    'product_id': self.id,
                    'price': price,
                    'company_id': company_id,
                }
            )

        return history
