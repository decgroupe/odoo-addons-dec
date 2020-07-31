# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    final_location = fields.Char(
        'Final location',
        compute='_compute_final_location',
        help='Get final location name',
        readonly=True,
    )

    created_purchase_line_archive = fields.Integer(
        readonly=True,
        copy=False,
    )
    created_production_archive = fields.Integer(
        readonly=True,
        copy=False,
    )

    def _archive_purchase_line(self, values):
        if 'created_purchase_line_id' in values:
            if values['created_purchase_line_id']:
                values['created_purchase_line_archive'] = values[
                    'created_purchase_line_id']

    def _archive_production(self, values):
        if 'created_production_id' in values:
            if values['created_production_id']:
                values['created_production_archive'] = values[
                    'created_production_id']

    @api.model
    def create(self, values):
        self._archive_purchase_line(values)
        self._archive_production(values)
        stock_move = super().create(values)
        return stock_move

    @api.multi
    def write(self, values):
        self._archive_purchase_line(values)
        self._archive_production(values)
        if values.get('procure_method'):
            for move in self:
                _logger.info(
                    'Procure method of move %d for product %s set to %s',
                    move.id,
                    move.product_id.display_name,
                    values.get('procure_method'),
                )

        return super(StockMove, self).write(values)

    @api.depends('move_dest_ids', 'location_dest_id', 'product_id')
    def _compute_final_location(self):
        admin = self.user_has_groups('base.group_system')
        for move in self:
            move.final_location = move.location_dest_id.name
            move_dest_id = move.move_dest_ids and move.move_dest_ids[0] or False
            if move_dest_id and move.product_id.id == move_dest_id.product_id.id:
                final_location = move_dest_id.final_location
                if final_location:
                    if admin:
                        move.final_location += ' > ' + final_location
                    else:
                        move.final_location = final_location
