# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import api, fields, models
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    invoice_lines = fields.Many2many(
        domain="""[
            ('move_id.move_type', '=', 'out_invoice'),
            '|',
            ('product_id', '=', product_id),
            ('product_id', '=', False),
        ]"""
    )

    force_invoiced = fields.Boolean(
        string="Force invoiced",
        help="When you set this field, the sale line will be "
        "considered as fully billed, even when there may be ordered "
        "or delivered quantities pending to bill.",
        readonly=True,
        copy=False,
    )

    @api.depends("force_invoiced", "order_id.force_invoiced")
    def _compute_invoice_status(self):
        """Compute invoice status, taking into account line-level force_invoiced."""
        res = super()._compute_invoice_status()
        for line in self:
            if line.state == "draft":
                line.invoice_status = "no"
            elif (
                float_is_zero(
                    line.price_total, precision_rounding=line.currency_id.rounding
                )
                and line.order_id.force_invoiced
            ):
                line.invoice_status = "invoiced"
        for line in self.filtered("force_invoiced"):
            line.invoice_status = "invoiced"
        return res

    def action_force_invoiced(self):
        """Toggle force_invoiced on the sale order line."""
        for rec in self:
            rec.force_invoiced = not rec.force_invoiced
