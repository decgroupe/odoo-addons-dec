# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    cost_price = fields.Float(
        compute='_compute_prices',
        digits='Purchase Price',
    )

    unit_price = fields.Float(
        compute='_compute_prices',
        digits='Purchase Price',
    )

    public_price = fields.Float(
        compute='_compute_prices',
        digits='Purchase Price',
    )

    @api.depends(
        'product_id',
        'product_id.lst_price',
        'partner_id',
        'product_qty',
        'product_uom_id',
        'product_uom_id.factor',
    )
    def _compute_prices(self):
        for line in self:
            if line.product_id:
                line.unit_price = line.product_id.product_tmpl_id.get_purchase_price(
                    line.partner_id, line.product_uom_id
                )
                line.cost_price = line.unit_price * line.product_qty
                line.public_price = line.product_id.lst_price / line.product_uom_id.factor
