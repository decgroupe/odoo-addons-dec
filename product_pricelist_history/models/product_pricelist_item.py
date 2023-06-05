# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from odoo import _, api, fields, models, tools


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    # This method is a copy/paste of the one in:
    #   ./addons/product/models/product_pricelist.py
    # except that `_addto_history` has been added.
    # yapf: disable
    def _compute_price(self, price, price_uom, product, quantity=1.0, partner=False):
        """Compute the unit price of a product in the context of a pricelist application.
           The unused parameters are there to make the full context available for overrides.
        """
        def _addto_history(message):
            hkey = (product, quantity, partner)
            self.pricelist_id._addto_history(hkey, message)

        self.ensure_one()
        convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))
        _addto_history(_('Base price is now {} ({})').format(price, self.compute_price))
        if self.compute_price == 'fixed':
            price = convert_to_price_uom(self.fixed_price)
            _addto_history(_('Price (fixed) set to {}').format(price))
        elif self.compute_price == 'percentage':
            price = (price - (price * (self.percent_price / 100))) or 0.0
            _addto_history(_('Price (percentage) set to {}').format(price))
        else:
            # complete formula
            price_limit = price
            price = (price - (price * (self.price_discount / 100))) or 0.0

            if self.price_discount:
                _addto_history(_('Price discounted to {} ({}%)').format(price, self.price_discount))

            if self.price_round:
                price = tools.float_round(price, precision_rounding=self.price_round)
                _addto_history(_('Price rounded to {}').format(price))

            if self.price_surcharge:
                price_surcharge = convert_to_price_uom(self.price_surcharge)
                price += price_surcharge
                _addto_history(_('Price surcharge applied {} (+{})').format(price, price_surcharge))

            if self.price_min_margin:
                price_min_margin = convert_to_price_uom(self.price_min_margin)
                price = max(price, price_limit + price_min_margin)
                _addto_history(_('Price updated (minimum margin) to {}').format(price))

            if self.price_max_margin:
                price_max_margin = convert_to_price_uom(self.price_max_margin)
                price = min(price, price_limit + price_max_margin)
                _addto_history(_('Price updated (maximum margin) to {}').format(price))

        return price
    # yapf: enable
