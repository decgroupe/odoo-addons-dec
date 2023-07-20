# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        rec = super(PurchaseOrder, self).create(vals)
        # Look at `stock_rule.py` in the same folder for details
        if rec and self.env.context.get("run_buy", False) is True:
            rec.with_context(run_buy="postprocess")._buy_postprocess()
        return rec

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        res = super(PurchaseOrder, self).search(
            args, offset=offset, limit=limit, order=order, count=count
        )
        # Look at `stock_rule.py` in the same folder for details
        if res and self.env.context.get("run_buy", False) is True:
            res.with_context(run_buy="postprocess")._buy_postprocess()
        return res

    def _buy_postprocess(self):
        for rec in self:
            if self.env.context.get("buyer"):
                rec = rec.with_user(user=self.env.context.get("buyer"))
            if self.env.context.get("message_post_to_po"):
                rec.message_post(body=self.env.context.get("message_post_to_po"))
