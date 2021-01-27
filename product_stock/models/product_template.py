# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def search_inventory_done_at_location(self, create_date, location_id):
        query = """
            SELECT product_tmpl_id
            FROM stock_move
            WHERE product_tmpl_id IN (
                SELECT product_tmpl_id
                FROM stock_inventory_line
                WHERE create_date >= %s
            )
            AND (location_id = %s or location_dest_id = %s)
            GROUP BY product_tmpl_id;
        """
        self._cr.execute(query, (
            create_date,
            location_id,
            location_id,
        ))
        ids = list(map(lambda x: x[0], self._cr.fetchall()))
        return ids

    last_inventory_line = fields.Many2one(
        comodel_name='stock.inventory.line',
        compute='_compute_last_inventory',
    )

    last_inventory_quantity = fields.Char(
        compute='_compute_last_inventory',
    )

    last_inventory_date = fields.Datetime(compute='_compute_last_inventory', )

    def _get_last_inventory_line(self, location_id):
        self.ensure_one()
        return self.env['stock.inventory.line'].search(
            [
                ('product_id', 'in', self.product_variant_ids.ids),
                ('location_id', '=', location_id.id),
            ], 0, 1, 'id DESC'
        )

    def _compute_last_inventory(self):
        stock_location = self.env.ref('stock.stock_location_stock')
        for rec in self:
            rec.last_inventory_line = rec._get_last_inventory_line(
                stock_location
            )
            if rec.last_inventory_line:
                rec.last_inventory_quantity = '{} {}'.format(
                    rec.last_inventory_line.product_qty,
                    rec.last_inventory_line.product_uom_id.name,
                )
                last_inventory = self.env['stock.inventory'].search(
                    [
                        ('line_ids', 'in', rec.last_inventory_line.ids),
                        ('date', '!=', False),
                    ], 0, 1, 'date DESC'
                )
                if last_inventory:
                    rec.last_inventory_date = last_inventory.date
                else:
                    rec.last_inventory_date = False
