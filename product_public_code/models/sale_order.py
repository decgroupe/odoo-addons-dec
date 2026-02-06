# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        if self.product_id and self.product_id.public_code:
            # split name between product name and description
            name, separator, description = self.name.partition("\n")
            # reformat name to replace product default code with public code
            name = f"[{self.product_id.public_code}] {self.product_id.name}"
            self.name = f"{name}{separator}{description}"
