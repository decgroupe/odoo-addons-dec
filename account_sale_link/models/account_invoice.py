# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

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
                # Also support comma separator
                if invoice.origin and "," in invoice.origin:
                    origins = [x.strip() for x in invoice.origin.split(',')]
                else:
                    origins = invoice.origin.split()
                orders = self.env['sale.order'].search(
                    [('name', 'in', origins)]
                )
                invoice.sale_order_ids = orders
                invoice.sale_order_count = len(orders)

    @api.multi
    def action_view_sale_order(self):
        action = self.mapped('sale_order_ids').action_view()
        # override the context to get ride of the default filtering
        action['context'] = {}
        return action
