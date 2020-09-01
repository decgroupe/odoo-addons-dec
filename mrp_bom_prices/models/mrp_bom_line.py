# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    cost_price = fields.Float(
        compute='_compute_prices',
        digits=dp.get_precision('Purchase Price'),
    )

    unit_price = fields.Float(
        compute='_compute_prices',
        digits=dp.get_precision('Purchase Price'),
    )

    public_price = fields.Float(
        compute='_compute_prices',
        digits=dp.get_precision('Purchase Price'),
    )

    @api.multi
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
