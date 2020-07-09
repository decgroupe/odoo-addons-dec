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
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Jul 2020

from datetime import datetime

from odoo import api, fields, models, _


class MrpConsume(models.TransientModel):
    _name = "mrp.consume"
    _inherit = "mrp.product.produce"
    _description = "Consume Production"

    produce_line_ids = fields.One2many(
        'mrp.consume.line',
        'product_produce_id',
        string='Product to Track',
    )

    @api.multi
    def do_consume(self):
        # Check finished move where consumed move lines should be generated
        self.check_finished_move_lots()
        # Post inventory immediatly to execute _action_done on stock moves
        self.production_id.post_inventory()
        if self.production_id.state == 'confirmed':
            self.production_id.write(
                {
                    'state': 'progress',
                    'date_start': datetime.now(),
                }
            )
        return {'type': 'ir.actions.act_window_close'}

    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        super()._onchange_product_qty()
        # Override qty_done to 0 to allow the user to choose which
        # line he wants to validate and comsume
        for pl in self.produce_line_ids:
            pl.qty_done = 0

    @api.multi
    def action_minimize_qty_done(self):
        self.ensure_one()
        for pl in self.produce_line_ids:
            pl.qty_done = 0
        return self._reopen()

    @api.multi
    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        for pl in self.produce_line_ids:
            pl.qty_done = pl.qty_reserved
        return self._reopen()

    @api.multi
    def action_maximize_qty_done_to_consume(self):
        self.ensure_one()
        for pl in self.produce_line_ids:
            pl.qty_done = pl.qty_to_consume
        return self._reopen()

    @api.multi
    def _reopen(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'res_model': self._name,
            'target': 'new',
            'context': {
                'default_model': self._name,
            },
        }


class MrpConsumeLine(models.TransientModel):
    _name = "mrp.consume.line"
    _inherit = "mrp.product.produce.line"
    _description = "Consume Production Line"

    product_produce_id = fields.Many2one('mrp.consume')
    is_minimized = fields.Boolean(compute='_compute_is_m_status')
    is_maximized = fields.Boolean(compute='_compute_is_m_status')

    @api.depends('qty_done', 'qty_reserved', 'qty_to_consume')
    def _compute_is_m_status(self):
        for line in self:
            line.is_minimized = (line.qty_done == 0)
            line.is_maximized = (line.qty_done == line.qty_reserved) \
                                or (line.qty_done == line.qty_to_consume)

    @api.multi
    def action_minimize_qty_done(self):
        self.ensure_one()
        self.qty_done = 0
        return self.product_produce_id._reopen()

    @api.multi
    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        self.qty_done = self.qty_reserved
        return self.product_produce_id._reopen()