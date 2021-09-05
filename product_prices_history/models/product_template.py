# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

import logging

from odoo import api, fields, models, _
from odoo.tools.progressbar import progressbar as pb

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.multi
    def update_default_purchase_price(self):
        ''' Store default purchase prices which can be computed
            using different pricelist rules
        '''
        product_ids = self.with_context(active_test=False)\
            .mapped('product_variant_ids')
        for rec in pb(product_ids):
            rec.update_purchase_price(
                rec.default_purchase_price, fields.Datetime.now()
            )

    @api.multi
    def update_default_sell_price(self):
        ''' Store default sell prices which can be computed
            using different pricelist rules
        '''
        product_ids = self.with_context(active_test=False)\
            .mapped('product_variant_ids')
        for rec in pb(product_ids):
            rec.update_sell_price(rec.default_sell_price, fields.Datetime.now())

    def show_product_prices_history(self):
        self.ensure_one()
        product_ids = self.with_context(active_test=False)\
            .mapped('product_variant_ids')
        action = self.env.ref(
            'product_prices_history.product_prices_history_action'
        ).read()[0]
        action['domain'] = [
            ('product_id', 'in', product_ids.ids),
            ('type', '=', self._context.get('price_type')),
        ]
        action['context'] = {
            'default_product_id': product_ids.ids[0],
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
