# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from datetime import datetime

from odoo import api, fields, models
from odoo.tools import float_compare, float_round


class MrpConsumeLine(models.TransientModel):
    _name = "mrp.consume.line"
    _inherit = "mrp.product.produce.line"
    _description = "Consume Production Line"

    product_produce_id = fields.Many2one("mrp.consume")
    is_minimized = fields.Boolean(compute="_compute_is_m_status")
    is_maximized = fields.Boolean(compute="_compute_is_m_status")

    @api.depends("qty_done", "qty_reserved", "qty_to_consume")
    def _compute_is_m_status(self):
        for line in self:
            line.is_minimized = line.qty_done == 0
            line.is_maximized = (line.qty_done == line.qty_reserved) or (
                line.qty_done == line.qty_to_consume
            )

    def action_minimize_qty_done(self):
        self.ensure_one()
        self.qty_done = 0
        return self.product_produce_id._reopen()

    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        self.qty_done = self.qty_reserved
        return self.product_produce_id._reopen()
