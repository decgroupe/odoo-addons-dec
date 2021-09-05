# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from datetime import timedelta
from odoo import api, models, _, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picked_rate = fields.Float(
        compute='_compute_picked_rate',
        help='Rate of received raw products',
        store=True,
    )

    @api.multi
    @api.depends('move_raw_ids', 'note')
    def _compute_picked_rate(self):
        for rec in self:
            all_move_ids = rec.move_raw_ids.filtered(
                lambda x: x.state != 'cancel'
            )
            if all_move_ids:
                received_move_ids = all_move_ids.filtered(lambda x: x.received)
                rec.picked_rate = \
                    len(received_move_ids) * 100 / len(all_move_ids)

    @api.multi
    def action_update_picked_rate(self):
        self._compute_picked_rate()

    @api.multi
    def run_picked_rate_update_scheduler(self):
        date = fields.Datetime.to_string(
            fields.datetime.now() - timedelta(days=365)
        )
        production_ids = self.search(
            [
                ('picked_rate', '<', 100),
                ('write_date', '>=', date),
                ('state', '!=', 'cancel'),
            ]
        ).filtered('move_raw_ids')
        production_ids._compute_picked_rate()
