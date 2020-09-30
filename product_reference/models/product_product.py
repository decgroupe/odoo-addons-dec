# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Sep 2020

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # If name starts with a wilcard, then clear arg domain
        if name.startswith('*'):
            name = name[1:]
            args = False
        if not args:
            args = []
        # Make a search with default criteria
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        result = self.product_tmpl_id.append_public_code_search(name, result, limit)
        result = self.product_tmpl_id.append_reference_search(name, result, limit)
        return result
