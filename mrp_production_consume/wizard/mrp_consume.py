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


class MrpConsumeLine(models.TransientModel):
    _name = "mrp.consume.line"
    _inherit = "mrp.product.produce.line"
    _description = "Consume Production Line"

    product_produce_id = fields.Many2one('mrp.consume')
