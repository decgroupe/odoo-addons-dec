# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models, fields


class Product(models.Model):
    _inherit = 'product.product'

    last_move_id = fields.Many2one(
        'stock.move',
        compute='_compute_last_stock_move',
        string='Last Stock Move',
    )

    last_move_date = fields.Datetime(
        related='last_move_id.date',
        string='Last Stock Move Date',
    )

    def _compute_last_stock_move(self):
        for rec in self:
            move_id = self.env['stock.move'].search(
                [('product_id', '=', rec.id)],
                limit=1,
                order='date desc, id desc'
            )
            rec.last_move_id = move_id

    @api.model
    def search_inventory_done_at_location(self, create_date, location_id):
        query = """
            SELECT product_id
            FROM stock_move
            WHERE product_id IN (
                SELECT product_id
                FROM stock_inventory_line
                WHERE create_date >= %s
            )
            AND (location_id = %s or location_dest_id = %s)
            GROUP BY product_id;
        """
        self._cr.execute(query, (
            create_date,
            location_id,
            location_id,
        ))
        ids = list(map(lambda x: x[0], self._cr.fetchall()))
        return ids

    def _get_last_inventory_line(self, location_id):
        self.ensure_one()
        return self.env['stock.inventory.line'].search(
            [
                ('product_id', 'in', self.ids),
                ('location_id', '=', location_id.id),
            ], 0, 1, 'id DESC'
        )
