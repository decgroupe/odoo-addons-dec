# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def get_head_desc(self):
        head = "🧮{0}".format(self.name)
        # WARNING: the string character is a non-breaking space
        desc = "{} ≤ 𝜕 ≤ {} ↗ ×{}".format(
            self.product_min_qty,
            self.product_max_qty,
            self.qty_multiple,
        )
        return head, desc
