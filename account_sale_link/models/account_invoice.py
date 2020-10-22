# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    sale_order_ids = fields.One2many(
        comodel_name='sale.order',
        compute='_compute_sale_order',
    )
    sale_order_count = fields.Integer(
        compute='_compute_sale_order',
        string='Sale Order count',
        default=0,
        store=False,
    )

    @api.multi
    def _compute_sale_order(self):
        for invoice in self.filtered('origin'):
            if invoice.type == 'out_invoice':
                orders = self.env['sale.order'].search(
                    [('name', 'in', invoice.origin.split())]
                )
                invoice.sale_order_ids = orders
                invoice.sale_order_count = len(orders)

    @api.multi
    def action_view_sale_order(self):
        action = self.env.ref('sale.action_orders')
        result = action.read()[0]
        # override the context to get ride of the default filtering
        result['context'] = {}
        sale_order_ids = self.mapped('sale_order_ids')
        # choose the view_mode accordingly
        if not sale_order_ids or len(sale_order_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % (sale_order_ids.ids)
        elif len(sale_order_ids) == 1:
            res = self.env.ref('sale.view_order_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [
                    (state, view)
                    for state, view in result['views'] if view != 'form'
                ]
            else:
                result['views'] = form_view
            result['res_id'] = sale_order_ids.id
        return result
