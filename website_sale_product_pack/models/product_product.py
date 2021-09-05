# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

import logging

from odoo import fields, models, api
from odoo.osv import expression

_logger = logging.getLogger(__name__)

class Product(models.Model):
    _inherit = 'product.product'

    parent_pack_website_published = fields.Boolean(
        compute='_compute_parent_pack_website_published',
        search='_search_parent_pack_website_published',
    )

    @api.multi
    @api.depends('used_in_pack_line_ids')
    def _compute_parent_pack_website_published(self):
        for rec in self:
            parent_product_ids = rec.used_in_pack_line_ids.mapped(
                'parent_product_id'
            )
            rec.parent_pack_website_published = any(
                parent_product_ids.mapped('website_published')
            )


    def _search_parent_pack_website_published(self, operator, value):
        if not isinstance(value, bool) or operator not in ('=', '!='):
            _logger.warning('unsupported search on parent_pack_website_published: %s, %s', operator, value)
            return [()]

        if operator in expression.NEGATIVE_TERM_OPERATORS:
            value = not value

        # Need to be implemented, otherwise parent_pack_website_published
        # must not be used in domain filtering
