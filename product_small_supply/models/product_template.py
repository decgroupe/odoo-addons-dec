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
        move_ids = self.env["stock.move"]
        # check if the `type` field is modified
        if any("type" in vals and vals["type"] != prod_tmpl.type for prod_tmpl in self):
            existing_move_lines = self.env["stock.move.line"].search(
                [
                    ("product_id", "in", self.mapped("product_variant_ids").ids),
                    ("state", "in", ["partially_available", "assigned"]),
                ]
            )
            # To allow changing product type, we have to manually unreserve
            # current moves. We will try to reserve them again after the
            # conversion
            if existing_move_lines:
                move_ids = existing_move_lines.mapped("move_id")
                move_ids._do_unreserve()
            # if the new type is not `product` then disable small supply
            if vals["type"] != "product":
                vals["small_supply"] = False
        res = super().write(vals)
        # After type conversion, we try to reserve again. Note that it could
        # fail because when a consumable becomes a product, its quantity will
        # be counted
        if move_ids:
            move_ids._action_assign()
        return res

    def action_convert_consu_to_small_supply(self):
        product_variant_ids = self.mapped("product_variant_ids")
        product_variant_ids.action_convert_consu_to_small_supply()
