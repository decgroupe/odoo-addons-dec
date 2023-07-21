# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models


class SoftwareLicensePack(models.Model):
    _inherit = "software.license.pack"

    product_ids = fields.One2many(
        comodel_name="product.product",
        inverse_name="license_pack_id",
        string="Products",
        readonly=True,
    )
