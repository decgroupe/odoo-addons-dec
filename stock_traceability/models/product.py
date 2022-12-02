# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api, fields


def product_type_to_emoji(product_type):
    res = product_type
    if res == 'product':
        res = '➕'
    elif res == 'consu':
        res = '🧃'
    elif res == 'service':
        res = '🛎️'
    return res


class Product(models.Model):
    _inherit = "product.template"

    type_emoji = fields.Char(compute='_compute_type_emoji')

    def _compute_type_emoji(self):
        for rec in self:
            rec.type_emoji = product_type_to_emoji(rec.type)
