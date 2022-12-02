# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    market_bom_ids = fields.One2many(
        comodel_name='ref.market.bom',
        inverse_name='product_id',
        string='Market bill of materials and services',
    )
    # performance: market_bom_id provides prefetching on the first market
    # bom only
    market_bom_id = fields.Many2one(
        comodel_name='ref.market.bom',
        string='Market bill of materials and services',
        compute='_compute_market_bom_id',
    )

    @api.depends('market_bom_ids')
    def _compute_market_bom_id(self):
        for p in self:
            p.market_bom_id = p.market_bom_ids[:1].id
