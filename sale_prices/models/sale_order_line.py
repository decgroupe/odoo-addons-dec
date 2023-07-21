# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    """
    Purchase price is now computed from a function named `_compute_purchase_price`.
    Our implementation of it is a copy/paste except that `product_cost` is
    computed from `_get_purchase_price` instead of `product.standard_price`.
    """

    # addons/sale_margin/models/sale_order.py
    def _compute_purchase_price(self):
        super()._compute_purchase_price()
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product = line.product_id
            product_cost = line._get_purchase_price()
            if not product_cost:
                # If the standard_price is 0
                # Avoid unnecessary computations
                # and currency conversions
                if not line.purchase_price:
                    line.purchase_price = 0.0
                continue
            fro_cur = product.cost_currency_id
            to_cur = line.currency_id or line.order_id.currency_id
            if line.product_uom and line.product_uom != product.uom_id:
                product_cost = product.uom_id._compute_price(
                    product_cost,
                    line.product_uom,
                )
            line.purchase_price = (
                fro_cur._convert(
                    from_amount=product_cost,
                    to_currency=to_cur,
                    company=line.company_id or self.env.company,
                    date=line.order_id.date_order or fields.Date.today(),
                    round=False,
                )
                if to_cur and product_cost
                else product_cost
            )
            # The pricelist may not have been set, therefore no conversion
            # is needed because we don't know the target currency..

    def _get_purchase_price(self):
        # Overwrite this function if you don't want to base your
        # purchase price on the product `default_purchase_price` from `product_prices`
        self.ensure_one()
        return self.product_id.default_purchase_price
