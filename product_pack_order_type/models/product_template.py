# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sept 2020

from odoo import fields, models


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
        default="all",
    )

    def copy(self, default=None):
        """
        The field `pack_line_ids` cannot be copied by the ORM even with `copy=True` and
        even with `copy=True` on `parent_product_id` field.
        The only workaround is to copy the lines manually in the `copy` method (not
        copy_data, because we need the ID of the new product to set it in
        `parent_product_id` field.
        """
        self.ensure_one()
        if default is None:
            default = {}

        res = super().copy(default=default)
        # if previous product had pack lines, copy them and link them to the new product
        # WARNING: The `parent_product_id` field is related to `product.product` and
        # not `product.template`, so we need to get the variant ID.
        if self.pack_line_ids:
            _pack_lines = self.pack_line_ids.copy(
                {"parent_product_id": res.product_variant_id.id}
            )
        return res
