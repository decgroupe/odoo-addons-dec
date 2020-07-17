# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )

    @api.model
    def create(self, values):
        # Use sale_line_id from sale_stock module to retrieve partner_id
        if 'move_prod_id' in values and values['move_prod_id']:
            move_prod_id = self.env['stock.move'].browse(values['move_prod_id'])
            while move_prod_id:
                if move_prod_id.sale_line_id and move_prod_id.sale_line_id.order_id:
                    partner_id = move_prod_id.sale_line_id.order_id.partner_shipping_id or False
                    values['partner_id'] = partner_id.id
                    break
                move_prod_id = move_prod_id.move_dest_id
        production = super(MrpProduction, self).create(values)
        return production
