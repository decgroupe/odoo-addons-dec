# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2024

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

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

    @api.depends(
        "state",
        "price_reduce",
        "product_id",
        "invoice_lines",
        "invoice_lines.price_total",
        "qty_delivered",
        "product_uom_qty",
    )
    def _compute_amount_to_invoice_ordqty(self):
        """This function is similar of built-in `_compute_untaxed_amount_to_invoice`
        excepts that the considered quantity ignore delivered quantity and invoice
        amount is always recomputed regardless of invoice line move state .
        """
        for line in self:
            amount_to_invoice_excluded = 0.0
            amount_to_invoice_included = 0.0
            if line.state in ["sale", "done"]:
                price_excluded = 0.0
                price_included = 0.0
                # contrary to original built-in function, we don't care about the
                # product's `invoice_policy` (order, delivered)
                uom_qty_to_consider = line.product_uom_qty
                price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                if line.tax_id:
                    values = line.tax_id.compute_all(
                        price_reduce,
                        currency=line.order_id.currency_id,
                        quantity=uom_qty_to_consider,
                        product=line.product_id,
                        partner=line.order_id.partner_shipping_id,
                    )
                    price_excluded = values["total_excluded"]
                    price_included = values["total_included"]
                else:
                    price_excluded = price_reduce * uom_qty_to_consider
                    price_included = price_excluded

                # always recompute invoice price_subtotal and price_total computation
                # ignoring discount. Also note that we don't care if the invoice line
                # move_id's 'state is "posted" (contrary to `taxed_amount_invoiced`)
                amount_excluded = 0
                amount_included = 0
                for l in line.invoice_lines:
                    amount = (
                        l.currency_id._convert(
                            l.price_unit,
                            line.currency_id,
                            line.company_id,
                            l.date or fields.Date.today(),
                            round=False,
                        )
                        * l.quantity
                    )
                    if l.tax_ids:
                        values = l.tax_ids.compute_all(amount)
                        amount_excluded += values["total_excluded"]
                        amount_included += values["total_included"]
                    else:
                        amount_excluded += amount
                        amount_included += amount

                amount_to_invoice_excluded = max(price_excluded - amount_excluded, 0)
                amount_to_invoice_included = max(price_included - amount_included, 0)

            line.amount_to_invoice_ordqty_taxexcl = amount_to_invoice_excluded
            line.amount_to_invoice_ordqty_taxincl = amount_to_invoice_included
