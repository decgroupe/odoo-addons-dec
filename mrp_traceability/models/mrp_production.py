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

import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _generate_raw_moves(self, exploded_lines):
        moves = super(MrpProduction, self)._generate_raw_moves(exploded_lines)
        return moves

    def _generate_raw_move(self, bom_line, line_data):
        move = super(MrpProduction,
                     self)._generate_raw_move(bom_line, line_data)
        return move

    def _get_raw_move_data(self, bom_line, line_data):
        res = super(MrpProduction, self)._get_raw_move_data(bom_line, line_data)
        if res is not None:
            # Override source location in product is consumable
            if bom_line.product_id.type == 'consu':
                # Copy destination to source location to create a fake
                # move that will stay in Warehouse/Production location
                location = self.env['stock.location'].browse(
                    res['location_dest_id']
                )
                res['location_id'] = location.id
                res['warehouse_id'] = location.get_warehouse().id
            # Link move destination to production moves to-do, this hook is
            # only done to keep REF Manager stock.move compatibility with
            # legacy
            res['move_dest_ids'] = [(6, 0, self.move_finished_ids.ids)]
        return res
