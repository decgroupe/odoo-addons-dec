# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductPackLine(models.Model):
    _inherit = 'product.pack.line'


    @api.multi
    def get_purchase_order_line_vals(self, line, order):
        self.ensure_one()
        uom_qty = self.quantity * line.product_uom_qty
        line_vals = {
            'order_id': order.id,
            'procurement_group_id': order.group_id.id,
            'product_id': self.product_id.id or False,
            'pack_parent_line_id': line.id,
            'pack_depth': line.pack_depth + 1,
            'company_id': order.company_id.id,
            'pack_modifiable': line.product_id.pack_modifiable,
        }
        pol = line.new(line_vals)
        pol.onchange_product_id()
        pol.product_qty = pol.product_uom._compute_quantity(uom_qty, pol.product_id.uom_id)
        pol._onchange_quantity()
        vals = pol._convert_to_write(pol._cache)
        pack_price_types = {'totalized', 'ignored'}
        if (
            line.product_id.pack_type == 'detailed' and
            line.product_id.pack_component_price in pack_price_types
        ):
            vals['price_unit'] = 0.0
        vals.update(
            {
                'name': '%s%s' % ('🢖 ' * (line.pack_depth + 1), pol.name),
            }
        )
        return vals
