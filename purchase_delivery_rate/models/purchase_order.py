# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    picked_rate = fields.Float(
        compute="_compute_picked_rate",
        help="Rate of received products",
        store=True,
    )

    @api.depends("state", "order_line.qty_received", "order_line.product_qty")
    def _compute_picked_rate(self):
        """Compute the rate of order lines fully received (as a percentage)."""
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for rec in self:
            received_count = 0
            line_count = 0
            rec.picked_rate = 0
            for line in rec.order_line:
                if line.product_type == "consu" and line.product_qty > 0:
                    line_count += 1
                    if (
                        float_compare(
                            line.qty_received,
                            line.product_qty,
                            precision_digits=precision,
                        )
                        >= 0
                    ):
                        received_count += 1
            if line_count > 0:
                rec.picked_rate = received_count * 100 / line_count

    def action_update_picked_rate(self):
        """Recompute the picked_rate field for the current records."""
        self._compute_picked_rate()
