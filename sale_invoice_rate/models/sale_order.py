# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    amount_to_invoice_ordqty_taxexcl = fields.Monetary(
        string="To Invoice (excl. taxes)",
        compute="_compute_amount_to_invoice_ordqty",
        compute_sudo=True,
        store=True,
        help="Untaxed Amount to Invoice (based on ordered quantities)",
    )
    amount_to_invoice_ordqty_taxincl = fields.Monetary(
        string="To Invoice (incl. taxes)",
        compute="_compute_amount_to_invoice_ordqty",
        compute_sudo=True,
        store=True,
        help="Taxed Amount to Invoice (based on ordered quantities)",
    )
    invoicing_rate = fields.Float(
        compute="_compute_invoicing_rate",
        help="Invoicing Rate",
    )

    # is_downpayment??

    @api.depends("order_line.amount_to_invoice_ordqty_taxexcl")
    @api.depends("order_line.amount_to_invoice_ordqty_taxincl")
    def _compute_amount_to_invoice_ordqty(self):
        """Compute the total invoice amount for each sales order."""
        result = self.env["sale.order.line"].read_group(
            [("order_id", "in", self.ids)],
            [
                "amount_to_invoice_ordqty_taxexcl:sum",
                "amount_to_invoice_ordqty_taxincl:sum",
                "order_id",
            ],
            ["order_id"],
        )
        amounts_taxexcl = {
            item["order_id"][0]: item["amount_to_invoice_ordqty_taxexcl"]
            for item in result
        }
        amounts_taxincl = {
            item["order_id"][0]: item["amount_to_invoice_ordqty_taxincl"]
            for item in result
        }
        for order in self:
            order.amount_to_invoice_ordqty_taxexcl = amounts_taxexcl.get(order.id, 0)
            order.amount_to_invoice_ordqty_taxincl = amounts_taxincl.get(order.id, 0)

    def _compute_invoicing_rate(self):
        self.invoicing_rate = 0
        for rec in self:
            if rec.amount_total > 0:
                amount_invoiced = (
                    rec.amount_total - rec.amount_to_invoice_ordqty_taxincl
                )
                rec.invoicing_rate = amount_invoiced / rec.amount_total * 100
