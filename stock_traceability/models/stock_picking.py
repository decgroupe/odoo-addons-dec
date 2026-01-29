# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models

PICKING_STATE_SYMBOLS = {
    "draft": "🏳️",
    "waiting": "⛓️",
    "confirmed": "⏳",
    "assigned": "✳️",
    "done": "✅",
    "cancel": "❌",
}


class StockPicking(models.Model):
    _inherit = "stock.picking"

    state_symbol = fields.Char(
        compute="_compute_state_symbol",
    )

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = PICKING_STATE_SYMBOLS.get(rec.state, "")

    def get_head_desc(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        head = f"🗳️{self.name}"
        desc = f"{self.state_symbol}{state}"
        return head, desc
