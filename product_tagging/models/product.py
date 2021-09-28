# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class Product(models.Model):
    _inherit = 'product.template'

    tagging_ids = fields.Many2many(
        comodel_name='tagging.tags',
        relation='tagging_product_tmpl',
        column1='product_tmpl_id',
        column2='tag_id',
        string='Tags',
    )
