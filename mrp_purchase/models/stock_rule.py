# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    # Inherit addons/purchase_stock/models/stock_rule.py
    @api.multi
    def _prepare_purchase_order_line(
        self, product_id, product_qty, product_uom, values, po, partner
    ):
        res = super()._prepare_purchase_order_line(
            product_id, product_qty, product_uom, values, po, partner
        )
        if 'production_id' in values:
            res['production_ids'] = [(6, 0, values['production_id'].ids)]
        if 'bom_line_id' in values:
            res['bom_line_id'] = values['bom_line_id'].id
        return res
