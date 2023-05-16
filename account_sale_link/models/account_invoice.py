# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        compute="_compute_sale_order",
        groups="sales_team.group_sale_salesman",
    )
    sale_order_count = fields.Integer(
        compute="_compute_sale_order",
        string="Sale Order count",
        default=0,
        store=False,
        groups="sales_team.group_sale_salesman",
    )

    def _compute_sale_order(self):
        self.sale_order_ids = False
        self.sale_order_count = 0
        for rec in self.filtered("invoice_origin"):
            if rec.move_type == "out_invoice":
                # Also support comma separator
                if rec.invoice_origin and "," in rec.invoice_origin:
                    origins = [x.strip() for x in rec.invoice_origin.split(",")]
                else:
                    origins = rec.invoice_origin.split()
                orders = self.env["sale.order"].search([("name", "in", origins)])
                rec.sale_order_ids = orders
                rec.sale_order_count = len(orders)

    def action_view_sale_order(self):
        action = self.mapped("sale_order_ids").action_view()
        # override the context to get ride of the default filtering
        action["context"] = {}
        return action
