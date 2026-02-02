# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    # copy from odoo/addons/mrp/models/product.py with hard-coded date range
    # removed from domain
    def _compute_mrp_product_qty(self):
        """Compute manufactured qty without the 1-year date-range restriction."""
        domain = [
            # ("state", "=", "done"),
            ("product_id", "in", self.ids),
        ]
        read_group_res = self.env["mrp.production"]._read_group(
            domain, ["product_id"], ["product_uom_qty:sum"]
        )
        mapped_data = {product.id: qty for product, qty in read_group_res}
        for product in self:
            if not product.id:
                product.mrp_product_qty = 0.0
                continue
            product.mrp_product_qty = float_round(
                mapped_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding,
            )

    def action_view_mos(self):
        """Return action to view all MOs for this product, without state filter."""
        action = super().action_view_mos()
        action["domain"] = [
            # ("state", "=", "done"),
            ("product_id", "in", self.ids),
        ]
        return action
