# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models, fields


class Product(models.Model):
    _inherit = "product.product"

    last_move_id = fields.Many2one(
        comodel_name="stock.move",
        compute="_compute_last_stock_move",
        string="Last Stock Move (« New » or « Cancelled » states are excluded)",
    )
    # don't use related here, because last_move_id cannot be searched
    #   related="last_move_id.date"
    last_move_date = fields.Datetime(
        compute="_compute_last_inventory",
        string="Last Stock Move Date",
    )
    last_inventory_line_id = fields.Many2one(
        comodel_name="stock.inventory.line",
        compute="_compute_last_inventory",
    )
    last_inventory_quantity = fields.Char(
        compute="_compute_last_inventory",
    )
    # don't use related here, because last_inventory_line_id cannot be searched
    #   related="last_inventory_line_id.inventory_id.date"
    last_inventory_date = fields.Datetime(
        compute="_compute_last_inventory",
    )

    def _compute_last_stock_move(self):
        if not self:
            self.last_move_id = False
            self.last_move_date = False
            return
        # flush fields to make sure DB is up to date
        self.flush()
        # use a raw sql query to get the last stock move
        query = """
            SELECT id, product_id
            FROM (
                SELECT id, product_id, date, ROW_NUMBER()
                OVER (PARTITION BY product_id ORDER BY date DESC) AS rn
                FROM stock_move
                WHERE state NOT IN ('draft', 'cancel')
            ) ranked
            WHERE rn = 1 and product_id in %s;
        """
        self.env.cr.execute(query, [tuple(self.ids)])
        rows = self.env.cr.fetchall()
        # create a mapping between product_id and last stock_move database id
        product_last_move = {row[1]: row[0] for row in rows}
        for rec in self:
            move_id = product_last_move.get(rec.id)
            rec.last_move_id = self.env["stock.move"].browse(move_id)
            rec.last_move_date = rec.last_move_id.date

    @api.model
    def search_need_inventory_update(self, inventory_start_date):
        """The purpose of this method is to find all products that have stock moves
        but have not been inventoried since the given date.
        """
        # FIXME: the location_id should be passed as a parameter
        query = """
            SELECT product_id
            FROM stock_move
            WHERE product_id NOT IN (
                SELECT product_id
                FROM stock_inventory_line
                WHERE inventory_date >= %(date)s
            )
            AND state NOT IN ('draft', 'cancel')
            GROUP BY product_id;
        """
        self._cr.execute(query, {"date": inventory_start_date})
        ids = list(map(lambda x: x[0], self._cr.fetchall()))
        return ids

    @api.model
    def search_inventory_done_at_location(self, create_date, location_id):
        query = """
            SELECT product_id
            FROM stock_move
            WHERE product_id IN (
                SELECT product_id
                FROM stock_inventory_line
                WHERE inventory_date >= %(date)s
            )
            AND (location_id = %(location_id)s or location_dest_id = %(location_id)s)
            GROUP BY product_id;
        """
        self._cr.execute(
            query,
            {"date": create_date, "location_id": location_id},
        )
        ids = list(map(lambda x: x[0], self._cr.fetchall()))
        return ids

    def _compute_last_inventory(self):
        if not self:
            self.last_inventory_line_id = False
            self.last_inventory_date = False
            self.last_inventory_quantity = False
            return
        # FIXME: this ref does not exist in the stock module outside a demo database
        stock_location = self.env.ref("stock.stock_location_stock")
        # SQL query to get the last inventory line for all products at once and use a
        # dictionary to store the results
        query = """
            SELECT id, product_id
            FROM (
                SELECT id, product_id, inventory_date, ROW_NUMBER()
                OVER (PARTITION BY product_id ORDER BY inventory_date DESC) AS rn
                FROM stock_inventory_line
                WHERE location_id = %(location_id)s
                AND product_id IN %(product_ids)s
            ) ranked
            WHERE rn = 1;
            """
        self.env.cr.execute(
            query,
            {
                "product_ids": tuple(self.ids),
                "location_id": stock_location.id,
            },
        )
        rows = self.env.cr.fetchall()
        # create a mapping between product_id and last stock_inventory_line database id
        product_last_inventory = {row[1]: row[0] for row in rows}
        for rec in self:
            inventory_line_id = product_last_inventory.get(rec.id)
            rec.last_inventory_line_id = self.env["stock.inventory.line"].browse(
                inventory_line_id
            )
            if rec.last_inventory_line_id:
                rec.last_inventory_date = rec.last_inventory_line_id.inventory_id.date
                rec.last_inventory_quantity = "{} {}".format(
                    rec.last_inventory_line_id.product_qty,
                    rec.last_inventory_line_id.product_uom_id.name,
                )
            else:
                rec.last_inventory_date = False
                rec.last_inventory_quantity = False
