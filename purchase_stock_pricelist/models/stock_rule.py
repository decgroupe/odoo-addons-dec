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
        vals["price_unit"] = line._get_price_unit_by_quantity(
            line.order_id,
            product_id,
            vals["product_qty"],
            product_uom,
            line.taxes_id,
        )
        return vals
