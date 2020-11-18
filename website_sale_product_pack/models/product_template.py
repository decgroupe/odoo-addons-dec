# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    parent_pack_website_published = fields.Boolean(
        related='product_variant_ids.parent_pack_website_published'
    )
