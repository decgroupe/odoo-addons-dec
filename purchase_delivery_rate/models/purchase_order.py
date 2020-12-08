# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

from odoo import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    picked_rate = fields.Float(
        compute='_compute_picked_rate',
        help='Rate of received products',
        store=True,
    )

    @api.multi
    @api.depends('picking_ids', 'picking_ids.move_lines')
    def _compute_picked_rate(self):
        for purchase in self:
            all_move_ids = purchase.picking_ids.mapped('move_lines').filtered(
                lambda x: x.state != 'cancel'
            )
            if all_move_ids:
                received_move_ids = all_move_ids.filtered(
                    lambda x: x.state == 'done'
                )
                purchase.picked_rate = \
                    len(received_move_ids) * 100 / len(all_move_ids)
