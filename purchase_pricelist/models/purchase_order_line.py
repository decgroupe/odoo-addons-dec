# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # _get_display_price is inspired from the 'sale.order.line'
    # same name function
    @api.model
    def _get_display_price(self, product, pricelist_id):
        # For purchase pricelists, we don't care about the discount_policy
        # We always return the discounted price
        product = product.with_context(pricelist=pricelist_id.id)
        return product.price

    @api.model
    def _get_price_unit(self, product_id, pricelist_id, taxes_id, company_id):
        res = self.env["account.tax"]._fix_tax_included_price_company(
            self._get_display_price(product_id, pricelist_id),
            product_id.supplier_taxes_id,
            taxes_id,
            company_id,
        )
        return res

    @api.model
    def _get_price_unit_by_quantity(
        self, order_id, product_id, product_uom_qty, product_uom_id, taxes_id
    ):
        product = product_id.with_context(
            lang=order_id.partner_id.lang,
            partner=order_id.partner_id,
            quantity=product_uom_qty,
            date=order_id.date_order,
            pricelist=order_id.pricelist_id.id,
            uom=product_uom_id.id,
            fiscal_position=self.env.context.get("fiscal_position"),
        )
        res = self._get_price_unit(
            product, order_id.pricelist_id, taxes_id, order_id.company_id
        )
        return res

    def _is_editable(self):
        return True

    # _onchange_quantity is inspired from the 'sale.order.line'
    # product_id_change function
    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        super()._onchange_quantity()
        if (
            self._is_editable()  # purchase_product_pack compatibility
            and self.product_id
            and self.order_id.pricelist_id
            and self.order_id.partner_id
        ):
            self.price_unit = self._get_price_unit_by_quantity(
                self.order_id,
                self.product_id,
                self.product_uom_qty,
                self.product_uom,
                self.taxes_id,
            )

    def _suggest_quantity(self):
        super()._suggest_quantity()

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        if po and po.pricelist_id:
            taxes_id = self.env["account.tax"]
            if res.get("taxes_id") and len(res["taxes_id"][0]) == 3:
                taxes_id = taxes_id.browse(res["taxes_id"][0][2])
            price_unit = self.env["purchase.order.line"]._get_price_unit_by_quantity(
                po, product_id, product_qty, product_uom, taxes_id
            )
            res["price_unit"] = price_unit
        return res
