# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

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


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def get_head_desc(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        head = f"🛒{self.order_id.name}"
        desc = f"{self.order_id.state_symbol}{state}"
        return head, desc
