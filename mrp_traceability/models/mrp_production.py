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


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def _generate_moves(self):
        super()._generate_moves()
        for production in self:
            production.move_finished_ids._action_confirm()

    # Override _generate_finished_moves from addons/mrp/models/mrp_production.py
    # and remove move._action_confirm() from method since it will be called a
    # bit later in _generate_moves
    def _generate_finished_moves(self):
        move = self.env['stock.move'].create({
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'picking_type_id': self.picking_type_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.product_qty,
            'location_id': self.product_id.property_stock_production.id,
            'location_dest_id': self.location_dest_id.id,
            'company_id': self.company_id.id,
            'production_id': self.id,
            'warehouse_id': self.location_dest_id.get_warehouse().id,
            'origin': self.name,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'move_dest_ids': [(4, x.id) for x in self.move_dest_ids],
        })
        #move._action_confirm()
        return move

    def _get_raw_move_data(self, bom_line, line_data):
        res = super()._get_raw_move_data(bom_line, line_data)
        res['move_dest_ids'] = [(6, 0, self.move_finished_ids.ids)] 
        return res
