# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, fields, models


class HelpdeskTicketReference(models.Model):
    _name = "helpdesk.ticket.reference"
    _description = "Reference"

    ticket_id = fields.Many2one(
        comodel_name="helpdesk.ticket",
        string="Ticket",
        required=True,
    )

    model_ref_id = fields.Reference(
        selection=lambda self: self._selection_model(),
        string="Reference",
        required=True,
    )

    def _get_applicable_models(self):
        return [
            "helpdesk.ticket",
            # soft support for `product` module
            "product.product",
            # soft support for `purchase` module
            "purchase.order",
            "purchase.order.line",
            # soft support for `sale` module
            "sale.order",
            "sale.order.line",
            # soft support for `mrp` module
            "mrp.production",
            "mrp.bom",
        ]

    @api.model
    def _selection_model(self):
        def _translate(model):
            """Custom translate function since we need to get model._description
            translation
            """
            ir_model_id = self.env["ir.model"].search([("model", "=", model)], limit=1)
            if ir_model_id:
                description = ir_model_id.name
            else:
                description = self.env[model]._description
            return f"{description} ({model})"

        res = [
            (x, _translate(x)) for x in self._get_applicable_models() if x in self.env
        ]
        return res
