# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import progressbar

from odoo import api, models, fields, _


class Product(models.Model):
    _inherit = "product.product"

    qty_available_cache = fields.Float('Quantity On Hand (Cache)', )

    last_move_id = fields.Many2one(
        'stock.move',
        compute='_compute_last_stock_move',
        string='Last Stock Move',
    )

    last_move_date = fields.Datetime(
        related='last_move_id.date',
        string='Last Stock Move Date',
    )

    @api.multi
    def _compute_last_stock_move(self):
        for rec in self:
            move_id = self.env['stock.move'].search(
                [('product_id', '=', rec.id)],
                limit=1,
                order='date desc, id desc'
            )
            rec.last_move_id = move_id

    @api.multi
    def _compute_qty_available_cache(self):
        for rec in self:
            rec.qty_available_cache = rec.qty_available
