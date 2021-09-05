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
    market_markup_rate = fields.Float(
        'Markup rate',
        help='Used by REF manager Market',
    )
    market_material_cost_factor = fields.Float(
        'Material factor (PF)',
        help='Used by REF manager Market',
    )

