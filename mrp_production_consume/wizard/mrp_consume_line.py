# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020


from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare


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
    product_tracking = fields.Selection(
        related="product_id.tracking",
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
    )
    qty_to_consume = fields.Float(
        string="To Consume",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
    )
    qty_done = fields.Float(
        string="Consumed",
        digits=dp.get_precision("Product Unit of Measure"),
    )
    move_id = fields.Many2one(
        comodel_name="stock.move",
    )
    qty_reserved = fields.Float(
        string="Reserved",
        digits=dp.get_precision("Product Unit of Measure"),
    )

    @api.onchange("lot_id")
    def _onchange_lot_id(self):
        """When the user is encoding a produce line for a tracked product, we apply
        some logic to help him. This onchange will automatically switch `qty_done`
        to 1.0.
        """
        res = {}
        if self.product_id.tracking == "serial":
            self.qty_done = 1
        return res

    @api.onchange("qty_done")
    def _onchange_qty_done(self):
        """When the user is encoding a produce line for a tracked product, we apply
        some logic to help him. This onchange will warn him if he set `qty_done`
        to a non-supported value.
        """
        res = {}
        if self.product_id.tracking == "serial" and self.qty_done:
            if (
                float_compare(
                    self.qty_done,
                    1.0,
                    precision_rounding=self.move_id.product_id.uom_id.rounding,
                )
                != 0
            ):
                message = (
                    _(
                        "You can only process 1.0 %s of products with unique "
                        "serial number."
                    )
                    % self.product_id.uom_id.name
                )
                res["warning"] = {"title": _("Warning"), "message": message}
        return res

    @api.onchange("product_id")
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id

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
        return self.consume_id._reopen()

    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        self.qty_done = self.qty_reserved
        return self.consume_id._reopen()
