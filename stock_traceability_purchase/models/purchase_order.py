# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models

PURCHASE_STATE_SYMBOLS = {
    "draft": "🏳️",
    "sent": "📩",
    "to approve": "⏳",
    "purchase": "💲",
    "done": "✅",
    "cancel": "❌",
}


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state_symbol = fields.Char(
        compute="_compute_state_symbol",
    )

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = PURCHASE_STATE_SYMBOLS.get(rec.state, "")
