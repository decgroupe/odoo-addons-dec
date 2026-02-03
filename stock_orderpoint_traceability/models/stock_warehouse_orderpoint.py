# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def get_head_desc(self):
        head = f"🧮{self.name}"
        desc = f"{self.product_min_qty} ≤ 𝜕 ≤ {self.product_max_qty} ↗ ×{self.qty_multiple}"  # noqa: E501
        return head, desc
