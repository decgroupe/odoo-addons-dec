# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def create(self, values):
        production = super(MrpProduction, self).create(values)
        # Use sale_order_id from sale_mrp_production_request_link module
        # to retrieve partner_id
        sale_order_id = production.sale_order_id
        # If no sale found then use sale_line_id stored in stock moves
        if not sale_order_id and production.move_finished_ids:
            move_ids = production.move_finished_ids
            while move_ids and not sale_order_id:
                for move in move_ids:
                    if move.sale_line_id and move.sale_line_id.order_id:
                        sale_order_id = move.sale_line_id.order_id
                        break
                move_ids = move_ids.mapped('move_dest_ids')
        if sale_order_id:
            production.sale_order_id = sale_order_id
            production.partner_id = sale_order_id.partner_shipping_id
        return production
