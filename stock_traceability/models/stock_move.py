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

from datetime import datetime
from dateutil import relativedelta
from itertools import groupby
from operator import itemgetter

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = "stock.move"

    final_location = fields.Char(
        'Final location',
        compute='_compute_final_location',
        help='Quantity in the default UoM of the product',
        readonly=True,
    )

    @api.depends('move_dest_ids', 'location_dest_id', 'product_id')
    def _compute_final_location(self):
        admin = self.user_has_groups('base.group_system')
        for move in self:
            move.final_location = move.location_dest_id.name
            move_dest_id = move.move_dest_ids and move.move_dest_ids[0] or False
            if move_dest_id and (
                move.product_id.id == move_dest_id.product_id.id
            ):
                if admin:
                    move.final_location += ' > ' + move_dest_id.final_location
                else:
                    move.final_location = move_dest_id.final_location
