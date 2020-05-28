# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, May 2020

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def price_compute(
        self, price_type, uom=False, currency=False, company=False,
    ):
        prices = super().price_compute(price_type, uom, currency, company)
        # By applying the following formula, we assume that all product
        # prices that can be set on the product page are set in purchase
        # Unit Of Measure (uom_po_id):
        for product in self:
            prices[product.id] = product.uom_po_id._compute_price(
                prices[product.id],
                product.uom_id,
            )
        return prices
