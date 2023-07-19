# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    market_bom_ids = fields.One2many(
        related="product_variant_ids.market_bom_ids",
    )
    market_bom_id = fields.Many2one(
        related="product_variant_ids.market_bom_id",
    )
