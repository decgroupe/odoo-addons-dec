# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import api, models, fields


class Product(models.Model):
    _inherit = 'product.template'

    favorite_ok = fields.Boolean(
        'Is a favorite',
        default=False,
        readonly=True,
        help="Technical field automatically computed used to find a product "
        "already used on a sale, a purchase or on a BoM"
    )

    @api.model
    def autoset_ok(self):
        # When autoset_ok is called, _set_attribute_ok is hooked to set
        # favorite_ok on already sold or puchased products
        super().autoset_ok()
        # In the same way, BoMs are browsed to compute `favorite_ok`
        self._autoset_favorite_ok()

    @api.model
    def _set_attribute_ok(self, ok_attribute, product_ids):
        super()._set_attribute_ok(ok_attribute, product_ids)
        if ok_attribute in ('sale_ok', 'purchase_ok'):
            self._set_favorite_ok(product_ids)

    @api.model
    def _autoset_favorite_ok(self):
        # Search among all existing BoMs
        mrp_bom_line_ids = self.env['mrp.bome.line'].read_group(
            [], ['product_id'], ['product_id']
        )
        # Assemble all products IDs
        product_ids = []
        for l in mrp_bom_line_ids:
            if l and l['product_id']:
                product_ids.append(l['product_id'][0])

        self._set_favorite_ok(product_ids)

    @api.model
    def _set_favorite_ok(self, product_ids):
        self._set_attribute_ok('favorite_ok', product_ids)
