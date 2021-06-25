# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    reference_id = fields.Many2one(
        'ref.reference',
        'Reference',
        compute='_compute_reference_id',
        readonly=True,
    )
    reference_ids = fields.One2many(
        'ref.reference',
        'product_id',
        string='References',
    )

    @api.multi
    @api.depends('reference_ids')
    def _compute_reference_id(self):
        for product in self:
            if len(product.reference_ids) > 0:
                product.reference_id = product.reference_ids[0]

    @api.model
    def append_extra_search(self, model, name, name_search_result, limit=100):
        result = super().append_extra_search(model, name, name_search_result, limit)
        result = self.append_reference_search(model, name, result, limit)
        return result

    @api.model
    def append_reference_search(self, model, name, name_search_result, limit=100):
        result = name_search_result
        if name:
            # Make a specific search to find a product with version inside
            if not result and 'V' in name.upper():
                reference = name.upper().rpartition('V')
                if reference[0]:
                    res = []
                    products = self.env[model].search(
                        [('default_code', 'ilike', reference[0])], limit=limit
                    )
                    res = products.name_get()
                    result = res + result
        return result
