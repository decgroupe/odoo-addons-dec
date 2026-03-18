# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_supplier_url = fields.Char(
        string="Product Supplier URL",
        compute="_compute_product_supplier_url",
    )

    @api.depends(
        "partner_id",
        "product_id",
        "product_qty",
        "product_qty",
        "product_uom",
        "order_id.date_order",
    )
    def _compute_product_supplier_url(self):
        self.product_supplier_url = False
        for line in self:
            # use the same logic as `_compute_price_unit_and_date_planned_and_name` to
            # find the supplier info to get the URL
            params = line._get_select_sellers_params()
            seller = line.product_id._select_seller(
                partner_id=line.partner_id,
                quantity=line.product_qty,
                date=line.order_id.date_order and line.order_id.date_order.date(),
                uom_id=line.product_uom,
                params=params,
            )
            if seller and seller.url:
                line.product_supplier_url = seller.url
