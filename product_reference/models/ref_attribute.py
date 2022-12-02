# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import re

from odoo import fields, models, api, _
from odoo.osv import expression


class RefAttribute(models.Model):
    """ Description """

    _name = 'ref.attribute'
    _description = 'Attribute'
    _rec_name = 'name'
    _order = 'code'

    property_id = fields.Many2one(
        'ref.property',
        'Property (owner)',
        required=True,
        ondelete='cascade',
    )
    code = fields.Char(
        'Code',
        required=True,
    )
    name = fields.Char(
        'Name',
        required=True,
    )
    auto_inc = fields.Boolean(
        'Auto-increment',
        default=False,
    )

    @api.model
    def create(self, vals):
        attribute_id = super().create(vals)
        return attribute_id

    @api.onchange('code')
    def onchange_code(self):
        self.ensure_one()
        self.code = self.property_id.validate_value(self.code)

    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for attribute in self:
            name = ('[%s] %s') % (attribute.code, attribute.name)
            result.append((attribute.id, name))
        return result

    @api.model
    def _name_search(
        self, name, args=None, operator='ilike', limit=100, name_get_uid=None
    ):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            attribute_ids = []
            if operator in positive_operators:
                attribute_ids = self._search(
                    [('code', '=', name)] + args,
                    limit=limit,
                    access_rights_uid=name_get_uid
                )
            if not attribute_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL
                # search performance would be abysmal on a database with
                # thousands of matching products, due to the huge merge+unique
                # needed for the OR operator (and given the fact that the
                # 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give
                # much better performance
                attribute_ids = self._search(
                    args + [('code', operator, name)], limit=limit
                )
                if not limit or len(attribute_ids) < limit:
                    # we may underrun the limit because of dupes in the
                    # results, that's fine
                    limit2 = (limit - len(attribute_ids)) if limit else False
                    product2_ids = self._search(
                        args + [
                            ('name', operator, name),
                            ('id', 'not in', attribute_ids)
                        ],
                        limit=limit2,
                        access_rights_uid=name_get_uid
                    )
                    attribute_ids.extend(product2_ids)
            elif not attribute_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
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
                attribute_ids = self._search(
                    domain, limit=limit, access_rights_uid=name_get_uid
                )
            if not attribute_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    attribute_ids = self._search(
                        [('code', '=', res.group(2))] + args,
                        limit=limit,
                        access_rights_uid=name_get_uid
                    )
        else:
            attribute_ids = self._search(
                args, limit=limit, access_rights_uid=name_get_uid
            )
        return self.browse(attribute_ids).name_get()
