# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models
from odoo.tools.progressbar import progressbar as pb


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def update_default_purchase_price(self):
        """Store default purchase prices which can be computed
        using different pricelist rules
        """
        product_ids = self.with_context(active_test=False).mapped("product_variant_ids")
        for rec in pb(product_ids):
            rec.update_purchase_price(rec.default_purchase_price, fields.Datetime.now())

    def update_default_sell_price(self):
        """Store default sell prices which can be computed
        using different pricelist rules
        """
        product_ids = self.with_context(active_test=False).mapped("product_variant_ids")
        for rec in pb(product_ids):
            rec.update_sell_price(rec.default_sell_price, fields.Datetime.now())

    def show_product_prices_history(self):
        product_ids = self.with_context(active_test=False).mapped("product_variant_ids")
        return product_ids.show_product_prices_history()

    def write(self, vals):
        res = super().write(vals)
        if "list_price" in vals or "standard_price" in vals:
            self.update_default_sell_price()
            self.update_default_purchase_price()
        return res
