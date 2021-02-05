# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
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
            partner_id = sale_order_id.partner_shipping_id or False
            values['partner_id'] = partner_id.id
        production = super(MrpProduction, self).create(values)
        return production
