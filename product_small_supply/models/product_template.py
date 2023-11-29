# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    small_supply = fields.Boolean(
        string="Small Supply",
        help="If checked, then this product will be considered like a "
        "consumable stockable product",
    )

    is_consumable = fields.Boolean(compute="_compute_is_consumable")

    def _compute_is_consumable(self):
        for product in self:
            if product.type == "consu":
                product.is_consumable = True
            elif product.type == "product" and product.small_supply:
                product.is_consumable = True
            else:
                product.is_consumable = False

    def write(self, vals):
        if "type" in vals and vals["type"] != "product":
            vals["small_supply"] = False
        res = super().write(vals)
        return res
