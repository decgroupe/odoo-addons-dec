# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models, fields


class ProductTemplate(models.Model):
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
        mrp_bom_line_ids = self.env['mrp.bom.line'].read_group(
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

    def append_favorite_emoji(self, model, names):
        # Add emoji to quickly identify a favorite
        result = []
        for item in names:
            product = self.env[model].browse(item[0])[0]
            name_get = item[1]
            if product.favorite_ok:
                name_get = '%s %s' % (name_get, '📌')
            result.append((item[0], name_get))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        return self.append_favorite_emoji(self._name, names)
