# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    mrp_product_qty = fields.Float(
        'Manufactured', compute='_compute_mrp_product_qty'
    )

    # Copy from odoo/addons/mrp/models/product.py with hard-coded date range
    # removed from domain
    def _compute_mrp_product_qty(self):
        domain = [('state', '=', 'done'), ('product_id', 'in', self.ids)]
        read_group_res = self.env['mrp.production'].read_group(
            domain, ['product_id', 'product_uom_qty'], ['product_id']
        )
        mapped_data = dict(
            [
                (data['product_id'][0], data['product_uom_qty'])
                for data in read_group_res
            ]
        )
        for product in self:
            product.mrp_product_qty = float_round(
                mapped_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding
            )

    def action_view_mos(self):
        action = super().action_view_mos()
        action['context'] = {
            'search_default_last_year_mo_order': 0,
        }
        return action