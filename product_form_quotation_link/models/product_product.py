# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from datetime import timedelta

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

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
        date_from = fields.Datetime.to_string(
            fields.datetime.now() - timedelta(days=365)
        )
        domain = [
            ('state', 'in', ['draft', 'sent', 'to approve']),
            ('product_id', 'in', self.mapped('id')),
            ('date_order', '>', date_from)
        ]
        order_lines = self.env['purchase.order.line'].read_group(
            domain, ['product_id', 'product_uom_qty'], ['product_id']
        )
        purchased_data = dict(
            [
                (data['product_id'][0], data['product_uom_qty'])
                for data in order_lines
            ]
        )
        for product in self:
            product.qty_in_purchase_quotation = float_round(
                purchased_data.get(product.id, 0),
                precision_rounding=product.uom_id.rounding
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
