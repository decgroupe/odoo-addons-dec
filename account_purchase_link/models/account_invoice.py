# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    purchase_order_ids = fields.One2many(
        comodel_name='purchase.order',
        compute='_compute_purchase_order',
    )
    purchase_order_count = fields.Integer(
        compute='_compute_purchase_order',
        string='Purchase Order count',
        default=0,
        store=False,
    )

    @api.multi
    def _compute_purchase_order(self):
        for invoice in self.filtered('origin'):
            if invoice.type == 'in_invoice':
                orders = self.env['purchase.order'].search(
                    [('name', 'in', invoice.origin.split())]
                )
                invoice.purchase_order_ids = orders
                invoice.purchase_order_count = len(orders)

    @api.multi
    def action_view_purchase_order(self):
        action = self.env.ref('purchase.purchase_form_action')
        result = action.read()[0]
        # override the context to get ride of the default filtering
        result['context'] = {}
        purchase_order_ids = self.mapped('purchase_order_ids')
        # choose the view_mode accordingly
        if not purchase_order_ids or len(purchase_order_ids) > 1:
            result['domain'] = "[('id', 'in', %s)]" % (purchase_order_ids.ids)
        elif len(purchase_order_ids) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [
                    (state, view)
                    for state, view in result['views'] if view != 'form'
                ]
            else:
                result['views'] = form_view
            result['res_id'] = purchase_order_ids.id
        return result
