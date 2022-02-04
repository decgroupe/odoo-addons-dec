# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    market_bom_id = fields.Many2one(
        'ref.market.bom',
        'Market bill of materials and services',
    )
    market_bom_labortime = fields.Float(
        string='Labor Time',
        compute='_compute_market_bom_labortime',
        help='Labor hour(s) computed from market BoM',
        digits=(16, 2),
    )
    market_markup_rate = fields.Float(
        'Markup rate',
        help='Used by REF manager Market',
    )
    market_material_cost_factor = fields.Float(
        'Material factor (PF)',
        help='Used by REF manager Market',
    )

    @api.multi
    def _compute_market_bom_labortime(self):
        labor_service_ids = self.env['product.product'].\
            get_market_bom_labortime_services()
        for rec in self:
            rec.market_bom_labortime = 0
            for line in rec.market_bom_id.bom_lines:
                if line.product_id in labor_service_ids:
                    rec.market_bom_labortime += line._convert_qty_to_hours()
