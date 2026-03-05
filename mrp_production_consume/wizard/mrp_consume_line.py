# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models


class MrpConsumeLine(models.TransientModel):
    _name = "mrp.consume.line"
    _description = "Consume Production Line"

    consume_id = fields.Many2one(
        comodel_name="mrp.consume",
    )
    is_minimized = fields.Boolean(
        compute="_compute_is_m_status",
    )
    is_maximized = fields.Boolean(
        compute="_compute_is_m_status",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    qty_to_consume = fields.Float(
        string="To Consume",
        digits="Product Unit of Measure",
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
    )
    qty_done = fields.Float(
        string="Consumed",
        digits="Product Unit of Measure",
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
    )
    qty_reserved = fields.Float(
        string="Reserved",
        digits="Product Unit of Measure",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        """Set product UoM from product definition."""
        self.product_uom_id = self.product_id.uom_id.id

    @api.depends("qty_done", "qty_reserved", "qty_to_consume")
    def _compute_is_m_status(self):
        """Compute minimize/maximize button states."""
        for line in self:
            line.is_minimized = line.qty_done == 0
            line.is_maximized = (line.qty_done == line.qty_reserved) or (
                line.qty_done == line.qty_to_consume
            )

    def action_minimize_qty_done(self):
        self.ensure_one()
        self.qty_done = 0
        if self.consume_id:
            return self.consume_id._reopen()
        else:
            return True

    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        self.qty_done = self.qty_reserved
        if self.consume_id:
            return self.consume_id._reopen()
        else:
            return True
