# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    """
    WARNING: `_compute_margin` and `_get_purchase_price` should return same
    values since their content is exactly the same, so we need to take care
    of this behaviour ...
    """
    # FIXME: [MIG] 14.0: To rewrite entirely

    # # addons/sale_margin/models/sale_order.py
    # def _compute_margin(self, order_id, product_id, product_uom_id):
    #     res = super()._compute_margin(order_id, product_id, product_uom_id)
    #     purchase_price = self._get_purchase_price(
    #         order_id, product_id, product_uom_id, date=False
    #     )
    #     return purchase_price['purchase_price']

    # # addons/sale_margin/models/sale_order.py
    # @api.model
    # def _get_purchase_price(self, pricelist, product, product_uom, date):
    #     res = super()._get_purchase_price(pricelist, product, product_uom, date)
    #     frm_cur = self.env.user.company_id.currency_id
    #     to_cur = pricelist.currency_id
    #     purchase_price = product.default_purchase_price
    #     if product_uom != product.uom_id:
    #         purchase_price = product.uom_id._compute_price(
    #             purchase_price, product_uom
    #         )
    #     price = frm_cur._convert(
    #         purchase_price,
    #         to_cur,
    #         self.order_id.company_id or self.env.user.company_id,
    #         date or fields.Date.today(),
    #         round=False
    #     )
    #     return {'purchase_price': price}
