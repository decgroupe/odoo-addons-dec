# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import fields, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Copy from odoo/addons/mrp/models/product.py with hard-coded date range
    # removed from domain
    def _compute_mrp_product_qty(self):
        super()._compute_mrp_product_qty()
        domain = [
            # ("state", "=", "done"),
            ("product_id", "in", self.ids),
        ]
        read_group_res = self.env["mrp.production"].read_group(
            domain, ["product_id", "product_uom_qty"], ["product_id"]
        )
        mapped_data = dict(
            [
                (data["product_id"][0], data["product_uom_qty"])
                for data in read_group_res
            ]
        )
        for product in self:
            if not product.id:
                product.mrp_product_qty = 0.0
                continue
            product.mrp_product_qty = float_round(
                mapped_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding,
            )

    def action_view_mos(self):
        action = super().action_view_mos()
        action["domain"] = [
            # ("state", "=", "done"),
            ("product_id", "in", self.ids)
        ]
        return action
