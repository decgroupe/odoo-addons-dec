# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    orderpoint_ids = fields.One2many(
        comodel_name='stock.warehouse.orderpoint',
        inverse_name='product_tmpl_id',
        string='Minimum Stock Rules',
    )
