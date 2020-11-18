# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import fields, models, api


class Product(models.Model):
    _inherit = 'product.product'

    parent_pack_website_published = fields.Boolean(
        compute='_compute_parent_pack_website_published'
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
