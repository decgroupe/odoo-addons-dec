# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class Product(models.Model):
    _inherit = 'product.product'
    _name = _inherit

    tagging_ids = fields.Many2many(
        comodel_name='tagging.tags',
        relation='tagging_product',
        column1='product_id',
        column2='tag_id',
        string='Tags',
    )
