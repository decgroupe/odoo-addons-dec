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
from .emoji_helper import (
    production_to_emoji,
    purchase_to_emoji,
    stockmove_to_emoji,
    product_type_to_emoji,
)


class StockMove(models.Model):
    _inherit = 'stock.move'

    mrp_status = fields.Text(
        compute='_compute_mrp_status',
        string='Procurement status',
        default='',
        store=False,
    )

    def _get_mto_mrp_status(self, move):
        res = '❓(???)[{0}]'.format(move.state)
        if move.created_purchase_line_id:
            res = '🛒{0}[{1}]'.format(
                move.created_purchase_line_id.order_id.name,
                purchase_to_emoji(move.created_purchase_line_id),
            )
        elif move.created_production_id:
            res = '⚙️{0}[{1}]'.format(
                move.created_production_id.name,
                production_to_emoji(move.created_production_id),
            )
        return res

    def _get_mts_mrp_status(self, move):
        res = '📦[{0}]'.format(stockmove_to_emoji(move))
        if move.created_purchase_line_archive and not move.created_purchase_line_id:
            res = res + '\n' + '♻️PO canceled'
        elif move.created_production_archive and not move.created_production_id:
            res = res + '\n' + '♻️MO canceled'
        return res

    @api.multi
    def _compute_mrp_status(self):
        for move in self:
            res = '...'
            if move.procure_method == 'make_to_order':
                res = self._get_mto_mrp_status(move)
            elif move.procure_method == 'make_to_stock':
                res = self._get_mts_mrp_status(move)

            move.mrp_status = '{0}{1}:{2}'.format(
                product_type_to_emoji(move.product_type),
                move.id,
                res
            )
