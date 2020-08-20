# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

import re

from odoo import api, fields, models


class ProcurementException(models.Model):
    _name = 'procurement.exception'
    _description = "Procurement Exception"
    _order = "sequence, id"

    name = fields.Char()
    sequence = fields.Integer(
        'Sequence',
        default=lambda self: self._default_sequence(),
        help="Gives the sequence order when displaying."
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        ondelete='cascade',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        ondelete='cascade',
        help="Specify a product if this rule only applies to one product. Keep \
empty otherwise."
    )
    categ_id = fields.Many2one(
        'product.category',
        'Product Category',
        ondelete='cascade',
        help="Specify a product category if this rule only applies to \
products belonging to this category or its children categories. Keep empty \
otherwise."
    )
    regex_pattern = fields.Char(
        string='RegEx',
        help="Regular Expression used to parse procurement exception message",
        oldname='message_regex'
    )

    @api.model
    def _default_sequence(self):
        rule = self.search([], limit=1, order="sequence DESC")
        return rule.sequence + 1

    def match(self, product_id, message):
        self.ensure_one()
        res = False
        if product_id:
            if self.product_id:
                if product_id.id == self.product_id.id:
                    res = True
                else:
                    return False
            if self.categ_id and not res:
                cat = product_id.categ_id
                while cat:
                    if cat.id == self.categ_id.id:
                        res = True
                        break
                    cat = cat.parent_id
                if not cat:
                    return False
        if self.regex_pattern:
            matches = re.search(self.regex_pattern, message)
            res = matches and matches.group(0)
        return res
