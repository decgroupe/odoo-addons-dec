# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models

PRODUCT_TYPE_SYMBOLS = {
    "product": "➕",
    "consu": "🧃",
    "service": "🛎️",
    "combo": "🧩",
}


class Product(models.Model):
    _inherit = "product.template"

    type_symbol = fields.Char(
        compute="_compute_type_symbol",
    )

    def _compute_type_symbol(self):
        for rec in self:
            product_type = rec.type
            if product_type == "consu" and rec.is_storable:
                product_type = "product"
            rec.type_symbol = PRODUCT_TYPE_SYMBOLS.get(product_type, "")
