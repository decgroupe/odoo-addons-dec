# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_category(models.Model):
    """ Description """

    _name = 'ref.category'
    _description = 'Category'
    _rec_name = 'name'
    _order = 'code'

    code = fields.Char('Code', size=3, required=True)
    name = fields.Text('Name', required=True)
    product_category = fields.Many2one('product.category', 'Product category')
    description_template = fields.Text('Template', required=False)
    category_lines= fields.One2many('ref.category.line','category')

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
