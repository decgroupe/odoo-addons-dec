# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    # @api.model_create_multi
    # def create(self, vals_list):
    #     lines = super(StockMoveLine, self).create(vals_list)
    #     for line in lines:
    #         move = line.move_id
    #         if move.state == 'done':
    #             move.mapped('product_tmpl_id').update_qty_available_cache()
    #     return lines

    # @api.multi
    # def write(self, vals):
    #     res = super().write(vals)
    #     if 'qty_done' in vals:
    #         self.mapped('move_id').mapped('product_tmpl_id').\
    #             update_qty_available_cache()
    #     return res
