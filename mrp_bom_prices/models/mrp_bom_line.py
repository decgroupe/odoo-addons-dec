# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    cost_price = fields.Float(
        compute="_compute_prices",
        digits="Purchase Price",
    )
    unit_price = fields.Float(
        compute="_compute_prices",
        digits="Purchase Price",
    )
    public_price = fields.Float(
        compute="_compute_prices",
        digits="Purchase Price",
    )

    @api.depends(
        "product_id",
        "product_id.lst_price",
        "partner_id",
        "product_qty",
        "product_uom_id",
        "product_uom_id.factor",
    )
    def _compute_prices(self):
        self.unit_price = 0
        self.cost_price = 0
        self.public_price = 0
        for rec in self.filtered("product_id"):
            # Get purchase/cost price
            if rec.seller_id:
                price = rec.seller_id.list_price_unit
            else:
                price = rec.product_id.standard_price
            rec.unit_price = rec.product_id.uom_id._compute_price(
                price,
                rec.product_uom_id,
            )
            # Compute total cost price
            rec.cost_price = rec.unit_price * rec.product_qty
            # Compute public price
            rec.public_price = rec.product_id.uom_id._compute_price(
                rec.product_id.lst_price,
                rec.product_uom_id,
            )
