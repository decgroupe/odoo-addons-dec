# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from datetime import datetime

from odoo import Command, api, fields, models
from odoo.tools import float_round


class MrpConsume(models.TransientModel):
    _name = "mrp.consume"
    _description = "Consume Production"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="production_id.company_id",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )
    product_qty = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
    )
    line_ids = fields.One2many(
        comodel_name="mrp.consume.line",
        inverse_name="consume_id",
        string="Raw Materials to Consume",
    )

    @api.model
    def default_get(self, fields):
        """Initialize wizard with production order data and remaining quantities."""
        res = super().default_get(fields)
        if self._context and self._context.get("active_id"):
            production = self.env["mrp.production"].browse(self._context["active_id"])
            if "production_id" in fields:
                res["production_id"] = production.id
            if "product_id" in fields:
                res["product_id"] = production.product_id.id
            if "product_uom_id" in fields:
                res["product_uom_id"] = production.product_uom_id.id
            if "product_qty" in fields:
                res["product_qty"] = production.product_qty
        return res

    def do_consume(self):
        """Validate and consume selected raw materials."""
        move_ids = self._get_updated_move_ids()
        self.production_id._post_inventory_consume(move_ids)
        if self.production_id.state == "confirmed":
            self.production_id.write(
                {
                    "state": "progress",
                    "date_start": datetime.now(),
                }
            )
        return {"type": "ir.actions.act_window_close"}

    def _get_updated_move_ids(self):
        """Updated stock moves linked to consume lines"""
        move_ids = self.env["stock.move"]
        for line in self.line_ids:
            if line.qty_done:
                line.move_id.quantity = line.qty_done
                line.move_id.picked = True
                move_ids |= line.move_id
        return move_ids

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        """Auto-calculate raw material consumption lines based on product quantity."""
        lines = []
        qty_todo = self.product_uom_id._compute_quantity(
            self.product_qty, self.production_id.product_uom_id, round=False
        )
        # browse all raw material moves that are not done or cancelled, and note that
        # we don't have to calculate consumption lines based on remaining quantities
        # and unit factors since used quantities are automatically converted to done
        # quantities in the moves when consumed.
        for move in self.production_id.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        ):
            qty_to_consume = float_round(
                qty_todo * move.unit_factor,
                precision_rounding=move.product_uom.rounding,
            )
            lines.append(
                {
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "product_uom_id": move.product_uom.id,
                    "qty_to_consume": qty_to_consume,
                    "qty_reserved": move.quantity,
                    "qty_done": 0,
                }
            )
        self.line_ids = [Command.clear()] + [Command.create(x) for x in lines]

    def action_minimize_qty_done(self):
        """Clear all consumed quantities."""
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = 0
        return self._reopen()

    def action_maximize_qty_done_reserved(self):
        """Set all quantities to reserved amounts."""
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = pl.qty_reserved
        return self._reopen()

    def action_maximize_qty_done_to_consume(self):
        """Set all quantities to required amounts."""
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = pl.qty_to_consume
        return self._reopen()

    def action_remove_make_to_order(self):
        """Remove make-to-order lines from consumption."""
        self.ensure_one()
        self.line_ids = self.line_ids.filtered(
            lambda pl: pl.move_id.procure_method != "make_to_order"
        )
        return self._reopen()

    def _reopen(self):
        """Reopen the wizard after action."""
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "context": self._context,
        }
