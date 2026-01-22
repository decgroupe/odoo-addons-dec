# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models


class Product(models.Model):
    _inherit = "product.product"

    def action_view_pricelist_items(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "product_pricelist_analysis.act_window_product_pricelist_item"
        )
        context = dict(self.env.context)
        context.update(
            {
                # use template only to match `_compute_variant_item_count` computation.
                # note that if the variant is set, the template is also set on the rule
                "search_default_product_tmpl_id": self.product_tmpl_id.id,
                "default_applied_on": "0_product_variant",
            }
        )
        action["context"] = context
        return action

    def open_pricelist_rules(self):
        action = super().open_pricelist_rules()
        # override odoo default action to use our custom one
        # default action is very restrivtive and show only rules with fixed price
        action = self.action_view_pricelist_items()
        return action
