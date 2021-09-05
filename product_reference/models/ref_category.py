# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import re

from odoo import api, fields, models
from odoo.osv import expression


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
    name = fields.Char(
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
        help="This text is used to automatically generate the product "
        "description based on its properties",
        required=False,
    )
    category_line_ids = fields.One2many(
        'ref.category.line',
        'category_id',
        string="Category Lines",
        oldname='category_lines',
    )

    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code category must be unique !'),
    ]

    def _prepare_product_category_vals(self, cat_vals):
        parent_categ_id = self.env.user.company_id.main_product_category_id
        return {
            'name': cat_vals.get('name'),
            'parent_id': parent_categ_id.id,
        }

    @api.model
    def create(self, vals):
        product_category_id = vals.get('product_category_id')
        if not product_category_id:
            product_category_vals = self._prepare_product_category_vals(vals)
            product_category = self.env['product.category'].create(
                product_category_vals
            )
            vals['product_category_id'] = product_category.id
        category_id = super().create(vals)
        return category_id

    @api.multi
    def write(self, vals):
        name = vals.get('name')
        if name:
            for rec in self.filtered('product_category_id'):
                if rec.product_category_id.name == self.name:
                    rec.product_category_id.name = name
        res = super().write(vals)
        return res

    @api.onchange('code')
    def onchange_code(self):
        self.ensure_one()
        if self.code:
            self.code = self.code.upper()

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for category in self:
            name = ('[%s] %s') % (category.code, category.name)
            result.append((category.id, name))

        return result

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            category_ids = []
            if operator in positive_operators:
                category_ids = self._search(
                    [('code', '=', name)] + args,
                    limit=limit,
                    access_rights_uid=name_get_uid
                )
            if not category_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL
                # search performance would be abysmal on a database with
                # thousands of matching products, due to the huge merge+unique
                # needed for the OR operator (and given the fact that the
                # 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give
                # much better performance
                category_ids = self._search(
                    args + [('code', operator, name)], limit=limit
                )
                if not limit or len(category_ids) < limit:
                    # we may underrun the limit because of dupes in the
                    # results, that's fine
                    limit2 = (limit - len(category_ids)) if limit else False
                    product2_ids = self._search(
                        args + [
                            ('name', operator, name),
                            ('id', 'not in', category_ids)
                        ],
                        limit=limit2,
                        access_rights_uid=name_get_uid
                    )
                    category_ids.extend(product2_ids)
            elif not category_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR(
                    [
                        [
                            '&',
                            ('code', operator, name),
                            ('name', operator, name),
                        ],
                        [
                            '&',
                            ('code', '=', False),
                            ('name', operator, name),
                        ],
                    ]
                )
                domain = expression.AND([args, domain])
                category_ids = self._search(
                    domain, limit=limit, access_rights_uid=name_get_uid
                )
            if not category_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    category_ids = self._search(
                        [('code', '=', res.group(2))] + args,
                        limit=limit,
                        access_rights_uid=name_get_uid
                    )
        else:
            category_ids = self._search(
                args, limit=limit, access_rights_uid=name_get_uid
            )
        return self.browse(category_ids).name_get()