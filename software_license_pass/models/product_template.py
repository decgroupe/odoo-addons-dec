# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2022

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    license_pack_id = fields.Many2one(
        related="product_variant_ids.license_pack_id",
        readonly=False,
    )

    def write(self, vals):
        """We remove from product.product to avoid error."""
        _vals = vals.copy()
        if vals.get("license_pack_id", False):
            self.product_variant_ids.write(
                {"license_pack_id": vals.get("license_pack_id")}
            )
            _vals.pop("license_pack_id")
        return super().write(_vals)
