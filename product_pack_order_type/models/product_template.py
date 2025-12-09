# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sept 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pack_order_type = fields.Selection(
        [
            ("all", "All"),
            ("sale", "Sale"),
            ("purchase", "Purchase"),
        ],
        "Order Type",
        help="Product will be treated as a pack:\n"
        "* All: Everywhere\n"
        "* Sale: Only when added in a Sale Order\n"
        "* Purchase: Only when added in a Purchase Order",
    )

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        res = super().copy(default=default)
        if self.pack_line_ids:
            new_lines = []
            for line in self.pack_line_ids:
                new_lines.append(line.copy({"parent_product_id": res.id}).id)
        return res
