# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, models, fields


class Product(models.Model):
    _inherit = 'product.product'

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
