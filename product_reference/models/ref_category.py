# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class RefCategory(models.Model):
    """ Description """

    _name = 'ref.category'
    _description = 'Category'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char(
        'Code',
        size=3,
        required=True,
    )
    name = fields.Text(
        'Name',
        required=True,
    )
    product_category_id = fields.Many2one(
        'product.category',
        'Product category',
        oldname='product_category',
    )
    description_template = fields.Text(
        'Template',
        required=False,
    )
    category_line_ids = fields.One2many(
        'ref.category.line',
        'category_id',
        oldname='category_lines',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code category must be unique !'),
    ]

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for category in self:
            name = ('%s: %s') % (category.code, category.name)
            result.append((category.id, name))

        return result
