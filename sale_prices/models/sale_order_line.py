# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class SaleOrderLine(models.Model):
    """Override sale.order.line to use default_purchase_price from product_prices."""

    _inherit = "sale.order.line"

    def _compute_purchase_price(self):
        """Override to use `default_purchase_price` from `product_prices` module.
        Replaces the standard_price-based computation with `_get_purchase_price()`
        which returns the product's `default_purchase_price` from `product_prices`.
        """
        res = super()._compute_purchase_price()
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product = line.product_id
            product_cost = line._get_purchase_price()
            if not product_cost:
                line.purchase_price = 0.0
                continue
            # convert cost to the line UoM if needed
            if line.product_uom and line.product_uom != product.uom_id:
                product_cost = product.uom_id._compute_price(
                    product_cost,
                    line.product_uom,
                )
            line.purchase_price = line._convert_to_sol_currency(
                product_cost,
                product.cost_currency_id,
            )
        return res

    def _get_purchase_price(self):
        """Return the product's default_purchase_price from product_prices module.

        Override this method to change the source of the purchase price.
        """
        self.ensure_one()
        return self.product_id.default_purchase_price
