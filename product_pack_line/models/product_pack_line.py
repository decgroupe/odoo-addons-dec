# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProductPackLine(models.Model):
    _name = "product.pack.line"
    _inherit = _name

    product_name = fields.Char(
        related="product_id.name",
    )
    product_code = fields.Char(
        related="product_id.default_code",
    )
    product_uom_id = fields.Many2one(
        related="product_id.uom_po_id",
        readonly=True,
    )
    product_categ_id = fields.Many2one(
        related="product_id.categ_id",
    )
