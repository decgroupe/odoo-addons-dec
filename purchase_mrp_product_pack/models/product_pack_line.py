# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models


class ProductPackLine(models.Model):
    _inherit = "product.pack.line"

    def get_purchase_order_line_vals(self, line, order):
        vals = super().get_purchase_order_line_vals(line, order)
        vals.update({"procurement_group_id": order.group_id.id})
        pol = line.new(vals)
        prefix = "🢖 " * (line.pack_depth + 1)
        vals.update(
            {
                "name": f"{prefix}{pol.name}",
            }
        )
        return vals
