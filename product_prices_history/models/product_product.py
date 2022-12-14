# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import api, fields, models, _
from odoo.tools import float_compare, safe_eval
from odoo.tools.misc import split_every
from odoo.tools.progressbar import progressbar as pb

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    last_default_sell_price = fields.Monetary(
        compute='_compute_last_default_prices',
        string='Last Sell Price',
        digits='Product Price',
        help="Last sell price from history",
    )

    last_default_purchase_price = fields.Monetary(
        compute='_compute_last_default_prices',
        string='Last Purchase Price',
        digits='Purchase Price',
        help="Last purchase price from history",
    )

    def _compute_last_default_prices(self):
        prices_hist_ids = self.env['product.prices.history'].search(
            [('product_id', 'in', self.ids)]
        )
        for rec in self:
            domain = [
                ('id', 'in', prices_hist_ids.ids),
                ('product_id', '=', rec.id),
            ]

            price_hist_id = self.env['product.prices.history'].search(
                domain + [('type', '=', 'purchase')], limit=1
            )
            if price_hist_id:
                rec.last_default_purchase_price = price_hist_id.get_price(
                    'purchase'
                )
            else:
                rec.last_default_purchase_price = False

            price_hist_id = self.env['product.prices.history'].search(
                domain + [('type', '=', 'sell')], limit=1
            )
            if price_hist_id:
                rec.last_default_sell_price = price_hist_id.get_price('sell')
            else:
                rec.last_default_sell_price = False

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
    def _update_default_prices(self, product_ids):
        SPLIT = 500
        search_domain = [
            ('id', 'in', product_ids),
            ('type', '=', 'product'),
        ]

        products = self.search(
            search_domain + [
                ('|'),
                ('purchase_ok', '=', True),
                ('sale_ok', '=', True),
            ]
        )
        idx = 0
        for ids in pb(list(split_every(SPLIT, products.ids))):
            _logger.info(
                'Processing (%d -> %d)/%d', idx,
                min(idx + SPLIT, len(products.ids)), len(products.ids)
            )
            idx += SPLIT
            self.browse(ids).update_default_purchase_price()
            self.env.cr.commit()

        products = self.search(search_domain + [
            ('sale_ok', '=', True),
        ])
        idx = 0
        for ids in pb(list(split_every(SPLIT, products.ids))):
            _logger.info(
                'Processing (%d -> %d)/%d', idx,
                min(idx + SPLIT, len(products.ids)), len(products.ids)
            )
            idx += SPLIT
            self.browse(ids).update_default_sell_price()
            self.env.cr.commit()

    def update_default_prices(self):
        self._update_default_prices(self.ids)

    @api.model
    def scheduler_update_default_prices(self):
        ids_with_moves = self._get_product_ids_with_moves()
        self._update_default_prices(ids_with_moves)

    def update_default_purchase_price(self):
        ''' Store default purchase prices which can be computed
            using different pricelist rules
        '''
        for rec in pb(self):
            rec.update_purchase_price(
                rec.default_purchase_price, fields.Datetime.now()
            )

    def update_default_sell_price(self):
        ''' Store default sell prices which can be computed
            using different pricelist rules
        '''
        for rec in pb(self):
            rec.update_sell_price(rec.default_sell_price, fields.Datetime.now())

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

    def update_sell_price(self, price, date):
        precision = self.env['decimal.precision'].precision_get('Product Price')
        for rec in self.with_context(prefetch_fields=False):
            rec._update_price(
                price,
                precision,
                date,
                'sell',
            )

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
        product_ids = self
        action = self.env.ref(
            'product_prices_history.product_prices_history_action'
        ).read()[0]
        action['domain'] = [
            ('product_id', 'in', product_ids.ids),
            ('type', '=', self._context.get('price_type')),
        ]
        eval_ctx = {
            'active_id': product_ids.ids[0],
            'active_ids': product_ids.ids,
        }
        action['context'] = dict(safe_eval(action.get('context'), eval_ctx))
        action['context'].update(
            {
                'default_product_id': product_ids.ids[0],
                'default_type': self._context.get('price_type'),
                'product_prices_history_multi_view': len(product_ids.ids) > 1,
            }
        )
        return action

    def write(self, vals):
        res = super().write(vals)
        if 'list_price' in vals or 'standard_price' in vals:
            self.update_default_sell_price()
            self.update_default_purchase_price()
        return res
