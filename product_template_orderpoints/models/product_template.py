# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    orderpoint_ids = fields.One2many(
        'stock.warehouse.orderpoint',
        'product_tmpl_id',
        'Minimum Stock Rules',
    )
