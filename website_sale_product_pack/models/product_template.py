# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    parent_pack_website_published = fields.Boolean(
        related="product_variant_ids.parent_pack_website_published"
    )
