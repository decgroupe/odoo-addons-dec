# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, OCt 2020

from odoo import api, models, _, fields


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picked_rate = fields.Float(
        compute='_compute_picked_rate',
        help='Rate of received raw products',
        store=True,
    )

    @api.multi
    @api.depends('move_raw_ids')
    def _compute_picked_rate(self):
        for production in self:
            all_move_ids = production.move_raw_ids.filtered(
                lambda x: x.state != 'cancel'
            )
            if all_move_ids:
                received_move_ids = all_move_ids.filtered(lambda x: x.received)
                production.picked_rate = \
                    len(received_move_ids) * 100 / len(all_move_ids)
