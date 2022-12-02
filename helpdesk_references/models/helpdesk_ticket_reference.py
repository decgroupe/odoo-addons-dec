# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

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

        def _translate(src):
            """ Custom translate function since we need to get
                model._description translation but the default gettext _ alias
                only search for `code` and `sql_constraint` translations
            """
            res = self.env['ir.translation'].sudo()._get_source(
                None, ('model', 'model_terms'), self.env.lang, src
            )
            return res

        return [
            (x, _translate(self.env[x]._description))
            for x in APPLICABLE_MODELS if x in self.env
        ]
