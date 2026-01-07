# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        # this method is only called when creating a PO from procurement
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        if po and po.pricelist_id:
            taxes_id = self.env["account.tax"]
            if res.get("taxes_id") and len(res["taxes_id"][0]) == 3:
                taxes_id = taxes_id.browse(res["taxes_id"][0][2])
            price_unit = self._get_price_unit(
                supplier.partner_id,
                po.pricelist_id,
                product_id,
                product_qty,
                product_uom,
                taxes_id,
                company_id=po.company_id,
            )
            res["price_unit"] = price_unit
        return res
