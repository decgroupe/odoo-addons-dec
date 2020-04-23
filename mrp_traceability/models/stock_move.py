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
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Apr 2020

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_status = fields.Text(
        compute='_compute_mrp_status',
        string='Procurement status',
        default='',
        store=False,
    )

    @api.multi
    def _compute_mrp_status(self):
        Production = self.env['mrp.production']
        for move in self:
            s = '...'
            if move.procure_method == 'make_to_order':
                if move.created_purchase_line_id:
                    s = '🛒{0}: [{1}]'.format(
                        move.created_purchase_line_id.order_id.name,
                        move.created_purchase_line_id.state,
                    )
                elif move.created_production_id:
                    #Production.browse(move.production_id)
                    s = '⚙️{0}: [{1}]'.format(
                            move.created_production_id.name,
                            move.created_production_id.state,
                        )
                else:
                    s = '📦[{0}] (procurement canceled)'.format(
                            move.state,
                        )
            elif move.procure_method == 'make_to_stock':
                s = '📦[{0}]'.format(
                        move.state,
                    )
            #move.picking_type_id
            if move.product_type == 'product':
                pass

            move.mrp_status = '{0}:{1}\n({2}){3}'.format(
                move.id,
                s,
                move.procure_method,
                move.product_type,
            )
