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
