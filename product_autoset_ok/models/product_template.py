# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, models


class Product(models.Model):
    _inherit = "product.template"

    @api.model
    def autoset_ok(self):
        """Automatically set `sale_ok` and `purchase_ok` to True for products used in
        sale or purchase orders
        """
        self._autoset_sale_ok()
        self._autoset_purchase_ok()

    @api.model
    def _autoset_sale_ok(self):
        """Assemble all products IDs by searching among all existing sale orders
        (any states)
        """
        product_ids = self.env["product.product"]
        for product_id, _count in self.env["sale.order.line"]._read_group(
            domain=[("product_id.sale_ok", "=", False)],
            groupby=["product_id"],
            aggregates=["__count"],
        ):
            product_ids |= product_id
        self._set_attribute_ok("sale_ok", product_ids)

    @api.model
    def _autoset_purchase_ok(self):
        """Assemble all products IDs by searching among all existing purchase orders
        (any states)
        """
        product_ids = self.env["product.product"]
        for product_id, _count in self.env["purchase.order.line"]._read_group(
            domain=[("product_id.purchase_ok", "=", False)],
            groupby=["product_id"],
            aggregates=["__count"],
        ):
            product_ids |= product_id
        self._set_attribute_ok("purchase_ok", product_ids)

    @api.model
    def _set_attribute_ok(self, ok_attribute, product_ids):
        # force `ok_attribute` to allow this product to be selectable if
        # filtered on this value
        if product_ids:
            product_ids.write({ok_attribute: True})
