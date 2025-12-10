# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    small_supply = fields.Boolean(
        string="Small Supply",
        help="If checked, then this product will be considered like a "
        "consumable stockable product",
    )

    is_consumable = fields.Boolean(compute="_compute_is_consumable")

    @api.depends("type", "is_storable", "small_supply")
    def _compute_is_consumable(self):
        for product in self:
            if product.type == "consu" and not product.is_storable:
                product.is_consumable = True
            elif (
                product.type == "consu"  # "product" type is now "consu+is_storable"
                and product.is_storable
                and product.small_supply
            ):
                product.is_consumable = True
            else:
                # FIXME: what about combo type?
                product.is_consumable = False

    def write(self, vals):
        if "is_storable" in vals and vals["is_storable"] is False:
            vals["small_supply"] = False
        res = super().write(vals)
        return res
