# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class MrpConsume(models.TransientModel):
    _name = "mrp.consume"
    _inherit = "mrp.product.produce"
    _description = "Consume Production"

    produce_line_ids = fields.One2many('mrp.consume.line', 'product_produce_id', string='Product to Track')

    @api.multi
    def do_consume(self):
        # Check finished move where consumed move lines should be generated
        self.check_finished_move_lots()
        # Post inventory immediatly to execute _action_done on stock moves
        self.production_id.post_inventory()
        if self.production_id.state == 'confirmed':
            self.production_id.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })
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