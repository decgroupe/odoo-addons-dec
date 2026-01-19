# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def write(self, vals):
        # trigger a check only if state or order lines are updated and if
        # the sale order is confirmed. Note that previously (Odoo <= 14.0), the check
        # was done on the line model _write, to "capture" related field updates, but
        # this is not working anymore as related field are pre-computed by the form
        # before writing the updated state.
        should_check_warn = vals.get("state") == "sale" or vals.get("order_line")
        res = super().write(vals)
        if res and self.state == "sale" and should_check_warn:
            self.mapped("order_line").mapped("product_id")._check_warn("block_confirm")
        return res
