# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        for rec, _vals in zip(record_ids, vals_list, strict=True):
            # look at `stock_rule.py` in the same folder for details
            if rec and self.env.context.get("run_buy", False) is True:
                rec.with_context(run_buy="postprocess")._buy_postprocess()
        return record_ids

    def write(self, values):
        if "group_id" in values:
            lines = self.env["purchase.order.line"]
            for order in self:
                lines += order.order_line.filtered(
                    lambda line: not line.procurement_group_id
                )
            if lines:
                lines.write({"procurement_group_id": values["group_id"]})
        return super().write(values)

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        res = super().search(args, offset=offset, limit=limit, order=order)
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
