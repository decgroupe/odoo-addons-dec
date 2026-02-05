# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

import logging

from odoo import api, fields, models
from odoo.tools import float_round

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    # marge_commerciale = prix_vente_HT - cout_achat_HT
    # - taux_marge = marge_commerciale/cout_achat_HT * 100
    # - taux_marque = marge_commerciale/prix_vente_HT * 100

    markup_percent = fields.Float(
        "Markup (%)",
        compute="_compute_markup",
        inverse="_inverse_markup_percent",
        store=True,
        groups="base.group_user",
        precompute=True,
        help="Markup percentage based on the cost price. "
        "It is computed as: (Unit Price - Cost Price) / Cost Price * 100",
    )

    @api.depends(
        "price_unit", "product_uom_qty", "purchase_price", "discount", "margin"
    )
    def _compute_markup(self):
        self.markup_percent = 0
        for line in self:
            if line.product_uom_qty > 0 and line.discount < 100 and line.price_unit > 0:
                margin = line.margin * 100 / line.product_uom_qty
                price = line.price_unit - (line.price_unit * line.discount / 100.0)
                line.markup_percent = margin / price

    # onchange method is needed to update the price unit when the user changes the
    # markup percent manually on the form view since the "inverse" method is only
    # called on "write"
    @api.onchange("markup_percent")
    def _inverse_markup_percent(self):
        line = self
        if (
            line.purchase_price > 0
            and line.discount < 100
            and line.markup_percent < 100
        ):
            discount_ratio = 1 - line.discount / 100.0
            markup_ratio = 1 - line.markup_percent / 100.0
            price = line.purchase_price / (discount_ratio * markup_ratio)
            line.price_unit = float_round(price, precision_digits=2)
        else:
            line.price_unit = 0
            line.markup_percent = 0
