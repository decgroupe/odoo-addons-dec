# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import progressbar

from odoo import api, models, fields, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    qty_available_cache = fields.Float('Quantity On Hand (Cache)', )

    @api.model
    def update_qty_available_cache(self):
        move_ids = self.env['stock.move'].search([])
        move_group = self.env['stock.move'].read_group(
            [('id', 'in', move_ids.ids)], ['product_id'], ['product_id'],
            lazy=False
        )
        product_ids = [x['product_id'][0] for x in move_group]
        records = self.search(
            [
                ('id', 'in', product_ids),
                ('type', '=', 'product'),
            ]
        )
        records._compute_qty_available_cache()

    @api.multi
    def _compute_qty_available_cache(self):
        with progressbar.ProgressBar(max_value=len(self)) as bar:
            for template in self:
                bar.update(bar.value + 1)
                product_ids = template.mapped('product_variant_ids')
                product_ids._compute_qty_available_cache()
                template.qty_available_cache = sum(
                    p.qty_available_cache for p in product_ids
                )
            bar.finish()
