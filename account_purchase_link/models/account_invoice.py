# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        compute="_compute_purchase_order",
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order",
        string="Purchase Order count",
        default=0,
        store=False,
    )

    def _compute_purchase_order(self):
        self.purchase_order_ids = False
        self.purchase_order_count = 0
        for invoice in self.filtered("invoice_origin"):
            if invoice.move_type == "in_invoice":
                orders = self.env["purchase.order"].search(
                    [("name", "in", invoice.invoice_origin.split())]
                )
                invoice.purchase_order_ids = orders
                invoice.purchase_order_count = len(orders)

    def action_view_purchase_order(self):
        action = self.mapped("purchase_order_ids").action_view()
        # override the context to get ride of the default filtering
        action["context"] = {}
        return action
