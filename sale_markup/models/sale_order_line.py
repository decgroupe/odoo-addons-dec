# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import logging
from odoo import api, fields, models
from odoo.tools import float_is_zero, float_round

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # taux_marge = marge_commerciale/cout_achat_HT * 100
    margin_percent = fields.Float(
        'Margin (%)', digits=(16, 2)
    )

     # taux_marque = marge_commerciale/prix_vente_HT * 100
    markup_percent = fields.Float(
        'Markup (%)', digits=(16, 2)
    )

    # Remove `price_unit` from @onchange to avoid price bouncing
    # with markup, margin, etc.
    @api.onchange('product_id', 'product_uom', 'product_uom_qty', 'tax_id')
    def _onchange_discount(self):
        previous_discount = self.discount
        super()._onchange_discount()
        if self.discount != previous_discount:
            _logger.info('_onchange_discount: %f -> %f', previous_discount, self.discount)
            

    @api.onchange('markup_percent')
    def onchange_markup_percent(self): 
        vals = {}
        if self.purchase_price > 0 and self.discount < 100:
            if self.markup_percent < 100: 
                new_price_unit = self.purchase_price / float(1-self.discount/100.0) / float(1-self.markup_percent/100.0) 
                new_price_unit = float_round(new_price_unit, precision_digits=2)
            else:
                new_price_unit = 0
                
            if hasattr(self, '_onchange_origin') and \
                self._onchange_origin in ('discount', 'price_unit'):
                # Do not update `price_unit` when `discount` is at the origin
                # of the @onchange event to avoid rounding issues
                # Note that `_onchange_origin` is set from function
                # `_update_markup_percent`
                pass
            else:
                vals.update({'price_unit': new_price_unit})
        else:
            vals.update({'markup_percent': 0})
            
        if 'markup_percent' in vals:
            _logger.info('onchange_markup_percent: set markup_percent=%f', vals.get('markup_percent'))
        if 'price_unit' in vals:
            _logger.info('onchange_markup_percent: set price_unit=%f', vals.get('price_unit'))

        self.update(vals)

    @api.onchange('purchase_price', 'product_uom_qty', 'price_unit', 'discount', 'margin')
    def _update_markup_percent(self):
        # Small hook to store origin if the @onchange event in a python object
        # attribute that will be automatically put into garbage at the end
        # of the @onchange propagation
        if hasattr(self, '_onchange_sender') and not hasattr(self, '_onchange_origin'):
            self._onchange_origin = self._onchange_sender

        vals = {}
        if (self.discount < 100) and (self.product_uom_qty > 0) and (self.price_unit > 0):
            new_markup_percent = self.margin/float(self.product_uom_qty) * 100 / float(self.price_unit - (self.price_unit * self.discount / 100.0))
        else:
            new_markup_percent = 0

        if not float_is_zero(new_markup_percent-self.markup_percent, precision_digits=2):
            _logger.info('_product_markup: set markup_percent=%f (sender=%s)', new_markup_percent, self._onchange_sender)
            vals.update({'markup_percent': new_markup_percent})
            self.update(vals)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        # Store current markup
        previous_markup_percent = self.markup_percent
        # Recompute price_unit
        super().product_uom_change()
        # Restore previous markup and update price_unit
        self.markup_percent = previous_markup_percent
        self.onchange_markup_percent()
