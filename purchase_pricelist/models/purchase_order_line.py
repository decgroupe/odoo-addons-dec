# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_round


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _compute_price_unit_and_date_planned_and_name(self):
        ids_to_super = set()
        for line in self:
            if not line.product_id or line.invoice_lines or not line.company_id:
                continue
            if line.order_id.pricelist_id:
                price_unit = self._get_price_unit(
                    line.partner_id,
                    line.order_id.pricelist_id,
                    line.product_id,
                    line.product_qty,
                    line.product_uom,
                    line.taxes_id,
                    line.order_id.company_id,
                )
                # use same rounding as in purchase module
                line.price_unit = float_round(
                    price_unit,
                    precision_digits=max(
                        line.currency_id.decimal_places,
                        self.env["decimal.precision"].precision_get("Product Price"),
                    ),
                )
                # reuse exact same code to get "date_planned"
                params = line._get_select_sellers_params()
                seller = line.product_id._select_seller(
                    partner_id=line.partner_id,
                    quantity=line.product_qty,
                    date=line.order_id.date_order
                    and line.order_id.date_order.date()
                    or fields.Date.context_today(line),
                    uom_id=line.product_uom,
                    params=params,
                )
                line.date_planned = line._get_date_planned(seller).strftime(
                    DEFAULT_SERVER_DATETIME_FORMAT
                )
            else:
                ids_to_super.add(line.id)
        # call super only for lines not managed by pricelist
        res = super(
            PurchaseOrderLine, self.browse(ids_to_super)
        )._compute_price_unit_and_date_planned_and_name()
        return res

    @api.model
    def _get_price_unit(
        self,
        supplier_id,
        pricelist_id,
        product_id,
        product_uom_qty,
        product_uom_id,
        taxes_id,
        company_id,
    ):
        price = pricelist_id.with_context(
            force_filter_supplier_id=supplier_id
        )._get_product_price(product_id, product_uom_qty, uom=product_uom_id)
        price_unit = self.env["account.tax"]._fix_tax_included_price_company(
            price,
            product_id.supplier_taxes_id,
            taxes_id,
            company_id,
        )
        return price_unit

    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, supplier, po
    ):
        # note that this method is called only when creating a PO from procurement.
        # this case is managed and tested by "purchase_stock_pricelist" module
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, company_id, supplier, po
        )
        return res
