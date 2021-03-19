# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021
from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    main_product_category_id = fields.Many2one(
        'product.category',
        'Main Product Category',
        ondelete='restrict',
    )
