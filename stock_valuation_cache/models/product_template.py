# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from datetime import timedelta
from odoo import api, models, fields, _
from odoo.tools.progressbar import progressbar as pb


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_cache = fields.Float('Quantity On Hand (Cache)', )

    def _get_product_ids_with_moves(self, since_date):
        moves = self.env['stock.move'].search(
            [('write_date', '>=', since_date)]
        )
        move_group = self.env['stock.move'].read_group(
            [('id', 'in', moves.ids)], ['product_id'], ['product_id'],
            lazy=False
        )
        return [x['product_id'][0] for x in move_group]

    @api.model
    def scheduler_update_qty_available_cache(self):
        # Recompute quantities only for product with moves in past 7 days
        # to speed up computation. Note that `update_qty_available_cache`
        # should be called once for all products with stock moves before
        # enabling this cron task
        since_date = fields.Datetime.now() + timedelta(days=-7)
        ids_with_moves = self._get_product_ids_with_moves(since_date)
        records = self.search(
            [
                ('id', 'in', ids_with_moves),
                ('type', '=', 'product'),
            ]
        )
        records.update_qty_available_cache()

    @api.multi
    def update_qty_available_cache(self):
        for rec in self:
            rec._compute_qty_available_cache()

    @api.multi
    def _compute_qty_available_cache(self):
        for template in pb(self):
            product_ids = template.mapped('product_variant_ids')
            product_ids._compute_qty_available_cache()
            template.qty_available_cache = sum(
                p.qty_available_cache for p in product_ids
            )
