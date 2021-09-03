# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa@decgroupe.com>, Sep 2021

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    action_reassign_visible = fields.Boolean(
        "Shows button to reassign",
        compute='_compute_action_reassign_visible',
        readonly=True,
    )

    def _compute_action_reassign_visible(self):
        for move in self:
            visible = move.quantity_done < move.product_uom_qty \
                and not move.is_locked \
                and move.state in [
                    'confirmed', 
                    'waiting', 
                    'partially_available',
                    'assigned'
                ]
            move.action_reassign_visible = visible

    @api.multi
    def action_assign(self):
        for move in self:
            move._action_assign()

    @api.multi
    def action_reassign(self):
        for move in self:
            move._do_unreserve()
            move._action_assign()

    @api.multi
    def action_recompute_state(self):
        self._recompute_state()

    @api.multi
    def action_force_state_confirmed_to_assigned(self):
        for move in self.filtered(lambda m: m.state == 'confirmed'):
            move.write({'state': 'assigned'})
