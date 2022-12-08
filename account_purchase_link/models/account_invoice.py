# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

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

    def _compute_purchase_order(self):
        for invoice in self.filtered('origin'):
            if invoice.type == 'in_invoice':
                orders = self.env['purchase.order'].search(
                    [('name', 'in', invoice.origin.split())]
                )
                invoice.purchase_order_ids = orders
                invoice.purchase_order_count = len(orders)

    def action_view_purchase_order(self):
        action = self.mapped('purchase_order_ids').action_view()
        # override the context to get ride of the default filtering
        action['context'] = {}
        return action
