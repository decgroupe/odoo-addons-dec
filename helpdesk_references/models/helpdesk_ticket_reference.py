# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import _, api, fields, models

APPLICABLE_MODELS = [
    'purchase.order',
    'purchase.order.line',
    'sale.order',
    'sale.order.line',
    'product.product',
    'mrp.production',
    'mrp.bom',
]


class HelpdeskTicketReference(models.Model):
    _name = 'helpdesk.ticket.reference'
    _description = "Reference"

    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        'Ticket',
        required=True,
    )

    model_ref_id = fields.Reference(
        selection='_selection_model',
        string='Reference',
        required=True,
    )

    @api.model
    def _selection_model(self):
        return [
            (x, _(self.env[x]._description))
            for x in APPLICABLE_MODELS if x in self.env
        ]
