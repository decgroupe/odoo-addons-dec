# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from datetime import datetime

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpConsume(models.TransientModel):
    _name = "mrp.consume"
    _description = "Consume Production"

    serial = fields.Boolean(
        string="Requires Serial",
    )
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
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )
    product_uom_id = fields.Many2one(
        comodel_name="uom.uom",
        string="Unit of Measure",
    )
    finished_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
    )
    line_ids = fields.One2many(  # was produce_line_ids
        comodel_name="mrp.consume.line",
        inverse_name="consume_id",
        string="Product to Track",
    )
    product_tracking = fields.Selection(
        related="product_id.tracking",
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        res = super(MrpConsume, self).default_get(fields)
        if self._context and self._context.get("active_id"):
            production = self.env["mrp.production"].browse(self._context["active_id"])
            serial_finished = production.product_id.tracking == "serial"
            todo_uom = production.product_uom_id.id
            if serial_finished:
                todo_quantity = 1.0
                if production.product_uom_id.uom_type != "reference":
                    todo_uom = (
                        self.env["uom.uom"]
                        .search(
                            [
                                (
                                    "category_id",
                                    "=",
                                    production.product_uom_id.category_id.id,
                                ),
                                ("uom_type", "=", "reference"),
                            ]
                        )
                        .id
                    )
            else:
                main_product_moves = production.move_finished_ids.filtered(
                    lambda x: x.product_id.id == production.product_id.id
                )
                todo_quantity = production.product_qty - sum(
                    main_product_moves.mapped("quantity_done")
                )
                todo_quantity = todo_quantity if (todo_quantity > 0) else 0
            if "production_id" in fields:
                res["production_id"] = production.id
            if "product_id" in fields:
                res["product_id"] = production.product_id.id
            if "product_uom_id" in fields:
                res["product_uom_id"] = todo_uom
            if "serial" in fields:
                res["serial"] = bool(serial_finished)
            if "product_qty" in fields:
                res["product_qty"] = todo_quantity
        return res

    def check_finished_move_lots(self):
        for line in self.line_ids:
            if line.qty_done:
                if line.product_id.tracking != "none" and not line.lot_id:
                    raise UserError(
                        _(
                            "Please enter a lot or serial number for %s !"
                            % line.product_id.display_name
                        )
                    )
                if not line.move_id:
                    # Find move_id that would match
                    move_id = self.production_id.move_raw_ids.filtered(
                        lambda m: m.product_id == line.product_id
                        and m.state not in ("done", "cancel")
                    )
                    if move_id:
                        line.move_id = move_id
                    else:
                        # create a move and put it in there
                        order = self.production_id
                        line.move_id = self.env["stock.move"].create(
                            {
                                "name": order.name,
                                "product_id": line.product_id.id,
                                "product_uom": line.product_uom_id.id,
                                "location_id": order.location_src_id.id,
                                "location_dest_id": self.product_id.property_stock_production.id,
                                "raw_material_production_id": order.id,
                                "group_id": order.procurement_group_id.id,
                                "origin": order.name,
                                "state": "confirmed",
                            }
                        )
                line.move_id.quantity_done = line.qty_done
                # line.move_id._generate_consumed_move_line(
                #     line.qty_done, self.lot_id, lot=line.lot_id
                # )
        return True

    def do_consume(self):
        # Check finished move where consumed move lines should be generated
        self.check_finished_move_lots()
        # Post inventory immediatly to execute _action_done on stock moves
        self.production_id._post_inventory()
        if self.production_id.state == "confirmed":
            self.production_id.write(
                {
                    "state": "progress",
                    "date_start": datetime.now(),
                }
            )
        return {"type": "ir.actions.act_window_close"}

    @api.onchange("product_qty")
    def _onchange_product_qty(self):
        lines = []
        qty_todo = self.product_uom_id._compute_quantity(
            self.product_qty, self.production_id.product_uom_id, round=False
        )
        # Do not filter out moves not linked to a bom_line_id
        for move in self.production_id.move_raw_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        ):
            qty_to_consume = float_round(
                qty_todo * move.unit_factor,
                precision_rounding=move.product_uom.rounding,
            )
            for move_line in move.move_line_ids:
                if (
                    float_compare(
                        qty_to_consume,
                        0.0,
                        precision_rounding=move.product_uom.rounding,
                    )
                    <= 0
                ):
                    break
                if (
                    float_compare(
                        move_line.product_uom_qty,
                        move_line.qty_done,
                        precision_rounding=move.product_uom.rounding,
                    )
                    <= 0
                ):
                    continue
                to_consume_in_line = min(qty_to_consume, move_line.product_uom_qty)
                lines.append(
                    {
                        "move_id": move.id,
                        "qty_to_consume": to_consume_in_line,
                        "qty_done": to_consume_in_line,
                        "lot_id": move_line.lot_id.id,
                        "product_uom_id": move.product_uom.id,
                        "product_id": move.product_id.id,
                        "qty_reserved": min(
                            to_consume_in_line, move_line.product_uom_qty
                        ),
                    }
                )
                qty_to_consume -= to_consume_in_line
            if (
                float_compare(
                    qty_to_consume, 0.0, precision_rounding=move.product_uom.rounding
                )
                > 0
            ):
                if move.product_id.tracking == "serial":
                    while (
                        float_compare(
                            qty_to_consume,
                            0.0,
                            precision_rounding=move.product_uom.rounding,
                        )
                        > 0
                    ):
                        lines.append(
                            {
                                "move_id": move.id,
                                "qty_to_consume": 1,
                                "qty_done": 1,
                                "product_uom_id": move.product_uom.id,
                                "product_id": move.product_id.id,
                            }
                        )
                        qty_to_consume -= 1
                else:
                    lines.append(
                        {
                            "move_id": move.id,
                            "qty_to_consume": qty_to_consume,
                            "qty_done": qty_to_consume,
                            "product_uom_id": move.product_uom.id,
                            "product_id": move.product_id.id,
                        }
                    )

        # In case of no lines were added, it could be because the production
        # order is done but some moves have been added after
        if qty_todo == 0 and not lines:
            for move in self.production_id.move_raw_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
                and float_compare(
                    m.quantity_done,
                    m.product_uom_qty,
                    precision_rounding=m.product_uom.rounding,
                )
                < 0
            ):
                for move_line in move.move_line_ids:
                    lines.append(
                        {
                            "move_id": move.id,
                            "qty_to_consume": move_line.product_uom_qty,
                            "qty_done": move_line.product_uom_qty,
                            "product_uom_id": move.product_uom.id,
                            "product_id": move.product_id.id,
                            "qty_reserved": move_line.product_uom_qty,
                        }
                    )
        self.line_ids = [(5,)] + [(0, 0, x) for x in lines]

        # Override qty_done to 0 to allow the user to choose which
        # line he wants to validate and comsume
        for pl in self.line_ids:
            pl.qty_done = 0

    def action_minimize_qty_done(self):
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = 0
        return self._reopen()

    def action_maximize_qty_done_reserved(self):
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = pl.qty_reserved
        return self._reopen()

    def action_maximize_qty_done_to_consume(self):
        self.ensure_one()
        for pl in self.line_ids:
            pl.qty_done = pl.qty_to_consume
        return self._reopen()

    def action_reopen(self):
        return self._reopen()

    def action_remove_make_to_order(self):
        self.ensure_one()
        line_ids = self.env["mrp.consume.line"]
        for pl in self.line_ids:
            if pl.move_id.procure_method != "make_to_order":
                line_ids += pl
        self.line_ids = line_ids
        return self._reopen()

    def action_generate_serial(self):
        self.ensure_one()
        self.finished_lot_id = self.env["stock.production.lot"].create(
            {
                "product_id": self.product_id.id,
                "company_id": self.production_id.company_id.id,
            }
        )
        return self._reopen()

    def _reopen(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": self.id,
            "res_model": self._name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }
