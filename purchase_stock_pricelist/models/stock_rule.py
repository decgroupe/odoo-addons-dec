# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if line.order_id.pricelist_id and line.price_unit:
            # remove updated price from vals since the right value has already
            # been set in "_prepare_purchase_order_line" method of
            # "purchase.order.line" model
            vals.pop("price_unit", None)
        return vals
