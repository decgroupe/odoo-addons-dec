# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class StockRule(models.Model):
    _inherit = "stock.rule"

    # Override addons/purchase_stock/models/stock_rule.py
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, partner
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner
        )
        if po and po.pricelist_id:
            if res.get("taxes_id") and len(res["taxes_id"][0]) == 3:
                taxes_id = self.env["account.tax"].browse(res["taxes_id"][0][2])
            else:
                taxes_id = self.env["account.tax"]

            price_unit = self.env["purchase.order.line"]._get_price_unit_by_quantity(
                po, product_id, product_qty, product_uom, taxes_id
            )
            res["price_unit"] = price_unit
        return res
