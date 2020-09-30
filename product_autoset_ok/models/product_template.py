# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Sep 2020

from odoo import api, models


class Product(models.Model):
    _inherit = 'product.template'

    @api.model
    def autoset_ok(self):
        self._autoset_sale_ok()
        self._autoset_purchase_ok()

    @api.model
    def _autoset_sale_ok(self):
        # Search among all existing sale orders (any states)
        sale_order_line_ids = self.env['sale.order.line'].read_group(
            [], ['product_id'], ['product_id']
        )
        # Assemble all products IDs
        product_ids = []
        for l in sale_order_line_ids:
            if l and l['product_id']:
                product_ids.append(l['product_id'][0])

        self._set_ok_attribute('sale_ok', product_ids)

    @api.model
    def _autoset_purchase_ok(self):
        # Search among all existing purchase orders (any states)
        purchase_order_line_ids = self.env['purchase.order.line'].read_group(
            [], ['product_id'], ['product_id']
        )
        # Assemble all products IDs
        product_ids = []
        for l in purchase_order_line_ids:
            if l and l['product_id']:
                product_ids.append(l['product_id'][0])

        self._set_ok_attribute('purchase_ok', product_ids)

    @api.model
    def _set_ok_attribute(self, ok_attribute, product_ids):
        # Find product template
        product_tmpl_ids = self.env['product.template'].with_context(
            active_test=False
        ).search(
            [
                ('product_variant_ids', 'in', product_ids),
                (ok_attribute, '=', False),
            ]
        )
        # Force `ok_attribute` to allow this product to be selectable if
        # filtered on this value
        product_tmpl_ids.write({ok_attribute: True})
