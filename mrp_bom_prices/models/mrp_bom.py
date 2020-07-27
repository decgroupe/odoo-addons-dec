# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    cost_price = fields.Float(
        compute='_compute_cost_price',
        digits=dp.get_precision('Purchase Price'),
    )

    @api.multi
    @api.depends('bom_line_ids.cost_price')
    def _compute_cost_price(self):
        for bom in self:
            prices = bom.bom_line_ids.mapped('cost_price')
            bom.cost_price = sum(prices)
