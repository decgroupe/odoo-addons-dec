# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import logging

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.tools.misc import split_every
from odoo.tools.progressbar import progressbar as pb
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_product_ids_with_moves(self):
        moves = self.env['stock.move'].search([])
        move_group = self.env['stock.move'].read_group(
            [('id', 'in', moves.ids)], ['product_id'], ['product_id'],
            lazy=False
        )
        return [x['product_id'][0] for x in move_group]

    def _get_product_ids_with_prices_history(self, price_type):
        prices = self.env['product.prices.history'].search(
            [('type', '=', price_type)]
        )
        price_group = self.env['product.prices.history'].read_group(
            [('id', 'in', prices.ids)], ['product_id'], ['product_id'],
            lazy=False
        )
        return [x['product_id'][0] for x in price_group]

    @api.model
    def scheduler_update_default_prices(self):
        # TODO: First search for the latest entry in history to get the most
        # recent date, then filter stock move by this date to reduce the
        # task charge
        # TODO: Also call update prices when a stock move is done (like it
        # is currently done for stock `real_time` valuation)

        SPLIT = 500
        ids_with_moves = self._get_product_ids_with_moves()

        search_domain = [
            ('id', 'in', ids_with_moves),
            ('type', '=', 'product'),
            ('purchase_ok', '=', True),
        ]

        products = self.search(
            search_domain + [
                ('purchase_ok', '=', True),
                # (
                #     'id', 'not in',
                #     self._get_product_ids_with_prices_history('purchase')
                # ),
            ]
        )
        idx = 0
        for ids in pb(split_every(SPLIT, products.ids)):
            idx += SPLIT
            _logger.info('Processing %d/%d', idx, len(products.ids))
            self.browse(ids).update_default_purchase_price()
            self.env.cr.commit()

        products = self.search(
            search_domain + [
                ('sale_ok', '=', True),
                # (
                #     'id', 'not in',
                #     self._get_product_ids_with_prices_history('sell')
                # ),
            ]
        )
        idx = 0
        for ids in pb(split_every(SPLIT, products.ids)):
            idx += SPLIT
            _logger.info('Processing %d/%d', idx, len(products.ids))
            self.browse(ids).update_default_sell_price()
            self.env.cr.commit()

    @api.multi
    def update_default_prices(self):
        self.update_default_purchase_price()
        self.update_default_sell_price()

    @api.multi
    def update_default_purchase_price(self):
        ''' Store default purchase prices which can be computed
            using different pricelist rules
        '''
        for rec in pb(self):
            rec.update_purchase_price(
                rec.default_purchase_price, fields.Datetime.now()
            )

    @api.multi
    def update_default_sell_price(self):
        ''' Store default sell prices which can be computed
            using different pricelist rules
        '''
        for rec in pb(self):
            rec.update_sell_price(rec.default_sell_price, fields.Datetime.now())

    @api.multi
    def update_purchase_price(self, price, date):
        precision = self.env['decimal.precision'].precision_get(
            'Purchase Price'
        )
        for rec in self.with_context(prefetch_fields=False):
            rec._update_price(
                price,
                precision,
                date,
                'purchase',
            )

    @api.multi
    def update_sell_price(self, price, date):
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for rec in self.with_context(prefetch_fields=False):
            rec._update_price(
                price,
                precision,
                date,
                'sell',
            )

    @api.multi
    def _update_price(self, price, precision, date, price_type):
        ''' Store prices which can be computed using different pricelist rules
        '''
        self.ensure_one()
        _logger.debug(
            'Updating %s price history of %s (%d)', price_type,
            self.display_name, self.id
        )

        company_id = self._context.get(
            'force_company', self.env.user.company_id.id
        )
        PricesHistory = self.env['product.prices.history']
        history = PricesHistory.search(
            [
                ('company_id', '=', company_id),
                ('product_id', '=', self.id),
                ('datetime', '<=', date),
                ('type', '=', price_type),
            ],
            order='datetime desc, id desc',
            limit=1
        )

        create = False
        if history:
            histprice = history.get_price(price_type)
            if float_compare(price, histprice, precision_digits=precision) != 0:
                create = True
        else:
            create = True

        if create:
            history = PricesHistory.create(
                {
                    'company_id': company_id,
                    'product_id': self.id,
                    'datetime': date,
                    'type': price_type,
                    price_type + '_price': price,
                }
            )

        return history

    def show_product_prices_history(self):
        self.ensure_one()
        action = self.env.ref(
            'product_prices_history.product_prices_history_action'
        ).read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('type', '=', self._context.get('price_type')),
        ]
        action['context'] = {
            'default_product_id': self.id,
            'default_type': self._context.get('price_type'),
        }
        return action

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'list_price' in vals or 'standard_price' in vals:
            self.update_default_sell_price()
            self.update_default_purchase_price()
        return res
