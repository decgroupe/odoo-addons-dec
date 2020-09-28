# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    public_code = fields.Char(
        'Public Code',
        size=24,
        oldname="ciel_code",
    )
    internal_notes = fields.Text(
        'Internal Notes',
        oldname='comments',
    )
    market_bom_id = fields.Many2one(
        'ref.market.bom',
        'Market bill of materials and services',
    )
    market_markup_rate = fields.Float(
        'Markup rate',
        help='Used by REF manager Market',
    )
    market_material_cost_factor = fields.Float(
        'Material factor (PF)',
        help='Used by REF manager Market',
    )
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
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        # Make a search with default criteria
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        result = self.append_public_code_search(name, result, limit)
        result = self.append_reference_search(name, result, limit)
        return result

    @api.model
    def append_public_code_search(self, name, name_search_result, limit=100):
        result = name_search_result
        if name:
            # Make a specific search according to public code
            products = self.search(
                [
                    ('public_code', 'ilike', name + '%'),
                    '|',
                    ('state', '!=', 'obsolete'),
                    ('state', '=', False),
                ],
                limit=limit
            )
            if products:
                res = []
                for product in products:
                    item = list(product.name_get()[0])
                    item[1] = ('%s (%s)') % (item[1], product.public_code)
                    res.append(item)
                result = res + result
        return result

    @api.model
    def append_reference_search(self, name, name_search_result, limit=100):
        result = name_search_result
        if name:
            # Make a specific search to find a product with version inside
            if not result and 'V' in name.upper():
                reference = name.upper().rpartition('V')
                if reference[0]:
                    res = []
                    products = self.search(
                        [('default_code', 'ilike', reference[0])], limit=limit
                    )
                    res = products.name_get()
                    result = res + result
        return result
