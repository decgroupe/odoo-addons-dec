# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2022

from odoo import models, api, _


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _run_buy(self, procurements):
        # Add a `run_buy` state var to the context before calling `_run_buy`.
        # Since base implementation search for an existing open purchase
        # order before creating it, we also override the `search` method of
        # the `purchase.order` to post a custom message if any. We also
        # override the `create` method for the same reason (when non existing
        # ourchase order is found).
        # Look at `purchase_order.py` in the same folder for more details.
        return super(
            StockRule, self.with_context(run_buy=True, buyer=self.env.user.id)
        )._run_buy(procurements)
