# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2020

from odoo import api, fields, models, _


class product_price_graph(models.TransientModel):
    _name = 'product.price.graph'
    _description = 'Customize purchase report'

    product_id = fields.Many2one('product.product')
    default_purchase_price_graph_po_uom = fields.Char(
        string='Purchase Price Graph',
        related='product_id.default_purchase_price_graph_po_uom'
    )
    default_sell_price_graph = fields.Char(
        string='Sell Price Graph',
        related='product_id.default_sell_price_graph'
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_ids = self.env.context.get('active_ids')
        if self.env.context.get('active_model') in (
            'product.template', 'product.product'
        ) and active_ids:
            res['product_id'] = active_ids[0]
        return res
