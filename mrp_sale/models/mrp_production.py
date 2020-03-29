# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
    )

    @api.model
    def create(self, values):
        # Use sale_line_id from sale_stock module to retrieve partner_id
        if values.has_key('move_prod_id') and values['move_prod_id'] != False:
            move_prod_id = self.env['stock.move'].browse(values['move_prod_id'])
            while move_prod_id:
                if move_prod_id.sale_line_id and move_prod_id.sale_line_id.order_id:
                    partner_id = move_prod_id.sale_line_id.order_id.partner_shipping_id or False
                    values['partner_id'] = partner_id.id
                    break
                move_prod_id = move_prod_id.move_dest_id
        production = super(MrpProduction, self).create(values)
        return production
