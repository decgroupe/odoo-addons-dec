# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_default_inventory_location(self):
        """Return the default internal stock location for the current company."""
        warehouse = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)],
            limit=1,
        )
        if warehouse:
            return warehouse.lot_stock_id
        return self.env["stock.location"].search(
            [
                ("usage", "=", "internal"),
                "|",
                ("company_id", "=", self.env.company.id),
                ("company_id", "=", False),
            ],
            order="company_id desc, id",
            limit=1,
        )

    last_move_id = fields.Many2one(
        comodel_name="stock.move",
        compute="_compute_last_stock_move",
        string="Last Stock Move (« New » or « Cancelled » states are excluded)",
    )
    last_move_date = fields.Datetime(
        compute="_compute_last_stock_move",
        string="Last Stock Move Date",
    )
    last_inventory_line_id = fields.Many2one(
        comodel_name="stock.quant",
        compute="_compute_last_inventory",
    )
    last_inventory_quantity = fields.Char(
        compute="_compute_last_inventory",
    )
    last_inventory_date = fields.Datetime(
        compute="_compute_last_inventory",
    )

    def _compute_last_stock_move(self):
        """Compute the latest non-draft stock move for each product."""
        if not self:
            self.last_move_id = False
            self.last_move_date = False
            return
        move_domain = [
            ("product_id", "in", self.ids),
            ("state", "not in", ["draft", "cancel"]),
        ]
        grouped_moves = self.env["stock.move"]._read_group(
            move_domain,
            ["product_id"],
            ["date:max"],
        )
        max_date_by_product = {
            product.id: max_date
            for product, max_date in grouped_moves
            if product and max_date
        }
        if not max_date_by_product:
            self.last_move_id = False
            self.last_move_date = False
            return
        candidate_moves = self.env["stock.move"].search(
            [
                *move_domain,
                ("product_id", "in", list(max_date_by_product.keys())),
                ("date", "in", list(set(max_date_by_product.values()))),
            ],
            order="product_id, date desc, id desc",
        )
        last_move_by_product = {}
        for move in candidate_moves:
            if move.date == max_date_by_product.get(move.product_id.id):
                last_move_by_product.setdefault(move.product_id.id, move)
        for rec in self:
            move = last_move_by_product.get(rec.id)
            rec.last_move_id = move
            rec.last_move_date = move.date if move else False

    @api.model
    def search_need_inventory_update(self, inventory_start_date):
        """Find products with stock moves that were not inventoried recently."""
        stock_location = self._get_default_inventory_location()
        if not stock_location:
            return []
        inventoried_products = set(
            self.search_inventory_done_at_location(
                inventory_start_date, stock_location.id
            )
        )
        grouped_moves = self.env["stock.move"]._read_group(
            [
                ("state", "not in", ["draft", "cancel"]),
                ("product_id", "not in", list(inventoried_products)),
            ],
            ["product_id"],
            ["__count"],
        )
        return [product.id for product, _count in grouped_moves if product]

    @api.model
    def search_inventory_done_at_location(self, create_date, location_id):
        """Find products inventoried at the requested location since a date."""
        create_date = fields.Datetime.to_datetime(create_date)
        grouped_moves = self.env["stock.move"]._read_group(
            [
                ("state", "=", "done"),
                ("is_inventory", "=", True),
                ("date", ">=", create_date),
                "|",
                ("location_id", "=", location_id),
                ("location_dest_id", "=", location_id),
            ],
            ["product_id"],
            ["__count"],
        )
        return [product.id for product, _count in grouped_moves if product]

    def _compute_last_inventory(self):
        """Compute the latest inventory values for each product."""
        self.last_inventory_line_id = False
        self.last_inventory_date = False
        self.last_inventory_quantity = False
        if not self:
            return
        stock_location = self._get_default_inventory_location()
        if not stock_location:
            return
        move_domain = [
            ("product_id", "in", self.ids),
            ("state", "=", "done"),
            ("is_inventory", "=", True),
            "|",
            ("location_id", "=", stock_location.id),
            ("location_dest_id", "=", stock_location.id),
        ]
        grouped_moves = self.env["stock.move"]._read_group(
            move_domain,
            ["product_id"],
            ["date:max"],
        )
        max_date_by_product = {
            product.id: max_date
            for product, max_date in grouped_moves
            if product and max_date
        }
        if not max_date_by_product:
            return
        candidate_moves = self.env["stock.move"].search(
            [
                *move_domain,
                ("product_id", "in", list(max_date_by_product.keys())),
                ("date", "in", list(set(max_date_by_product.values()))),
            ],
            order="product_id, date desc, id desc",
        )
        last_inventory_move_by_product = {}
        for inventory_move in candidate_moves:
            if inventory_move.date == max_date_by_product.get(
                inventory_move.product_id.id
            ):
                last_inventory_move_by_product.setdefault(
                    inventory_move.product_id.id,
                    inventory_move,
                )
        quant_by_product = {
            quant.product_id.id: quant
            for quant in self.env["stock.quant"].search(
                [
                    ("product_id", "in", list(max_date_by_product.keys())),
                    ("location_id", "=", stock_location.id),
                ],
                order="product_id, id desc",
            )
        }
        for rec in self:
            inventory_quant = quant_by_product.get(rec.id)
            inventory_move = last_inventory_move_by_product.get(rec.id)
            rec.last_inventory_line_id = inventory_quant
            if rec.last_inventory_line_id and inventory_move:
                rec.last_inventory_date = inventory_move.date
                rec.last_inventory_quantity = (
                    f"{rec.last_inventory_line_id.quantity} "
                    f"{rec.last_inventory_line_id.product_uom_id.name}"
                )
            else:
                rec.last_inventory_date = False
                rec.last_inventory_quantity = False
