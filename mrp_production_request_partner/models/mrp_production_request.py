# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

from odoo import models, api, fields


class MrpProductionRequest(models.Model):
    _inherit = 'mrp.production.request'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )
    zip_id = fields.Many2one(
        related='partner_id.zip_id',
        string='ZIP Location',
    )

    @api.model
    def create(self, values):
        # Same logic than mrp_sale
        sale_order_id = self.env['sale.order']
        # Use sale_order_id from sale_mrp_link module to retrieve partner_id
        if 'sale_order_id' in values and values['sale_order_id']:
            sale_order_id = sale_order_id.browse(values['sale_order_id'])
        # Use sale_line_id from sale_stock module to retrieve partner_id
        elif 'move_prod_id' in values and values['move_prod_id']:
            move_prod_id = self.env['stock.move'].browse(values['move_prod_id'])
            while move_prod_id:
                if move_prod_id.sale_line_id and move_prod_id.sale_line_id.order_id:
                    sale_order_id = move_prod_id.sale_line_id.order_id
                    break
                move_prod_id = move_prod_id.move_dest_id
        if sale_order_id:
            values['partner_id'] = sale_order_id.partner_shipping_id.id

        production_request = super().create(values)
        return production_request
