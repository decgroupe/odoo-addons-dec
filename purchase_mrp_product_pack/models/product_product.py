# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo import api, models


class ProductProdut(models.Model):
    _inherit = "product.product"

    def write(self, vals):
        res = super().write(vals)
        # automatically update the standard price of the pack products
        # when the standard price of one of its components changes
        # or when its pack settings are changed
        if not self.env.context.get("update_pack"):
            if (
                "standard_price" in vals
                or "pack_type" in vals
                or vals.get("pack_component_price") == "totalized"
            ):
                self._update_pack_standard_price()
        return res

    def _update_pack_standard_price(self):
        packs, no_packs = self.split_pack_products()
        packs |= no_packs.mapped("used_in_pack_line_ids").mapped("parent_product_id")
        for product in packs:
            if product.pack_type == "non_detailed" or (
                product.pack_type == "detailed"
                and product.pack_component_price == "totalized"
            ):
                pack_price = 0.0
                for pack_line in product.sudo().pack_line_ids:
                    pack_price += pack_line.get_standard_price()

                product.with_context(update_pack=True).standard_price = pack_price
