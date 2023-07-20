# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models


def sale_state_to_emoji(state):
    res = state
    if res == "draft":
        res = "🏳️"
    elif res == "sent":
        res = "📩"
    elif res == "sale":
        res = "💲"
    elif res == "done":
        res = "✅"
    elif res == "cancel":
        res = "❌"
    return res


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state_emoji = fields.Char(compute="_compute_state_emoji")

    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = sale_state_to_emoji(rec.state)
