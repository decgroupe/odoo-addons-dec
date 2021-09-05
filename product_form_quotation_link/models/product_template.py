# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    qty_in_purchase_quotation = fields.Float(
        compute='_compute_qty_in_purchase_quotation',
        string='In Purchase Quotation',
    )

    qty_in_sale_quotation = fields.Float(
        compute='_compute_qty_in_sale_quotation',
        string='In Sale Quotation',
    )
    
    @api.multi
    def _compute_qty_in_purchase_quotation(self):
        for template in self:
            template.qty_in_purchase_quotation = float_round(
                sum(
                    [
                        p.qty_in_purchase_quotation
                        for p in template.product_variant_ids
                    ]
                ),
                precision_rounding=template.uom_id.rounding
            )

    @api.multi
    def _compute_qty_in_sale_quotation(self):
        domain = [
            ('state', 'in', ['draft', 'sent']),
            ('product_id', 'in', self.mapped('id')),
        ]
        order_lines = self.env['sale.order.line'].read_group(
            domain, ['product_id', 'product_uom_qty'], ['product_id']
        )
        purchased_data = dict(
            [
                (data['product_id'][0], data['product_uom_qty'])
                for data in order_lines
            ]
        )
        for product in self:
            product.qty_in_sale_quotation = float_round(
                purchased_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding
            )
