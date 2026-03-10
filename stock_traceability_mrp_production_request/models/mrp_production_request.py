# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models

PRODUCTION_REQUEST_STATE_SYMBOLS = {
    "draft": "🏳️",
    "to_approve": "⏳",
    "approved": "🚧",
    "done": "✅",
    "cancel": "❌",
}


class ProductionRequest(models.Model):
    _inherit = "mrp.production.request"

    state_symbol = fields.Char(compute="_compute_state_symbol")

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = PRODUCTION_REQUEST_STATE_SYMBOLS.get(rec.state, "")

    def get_head_desc(self):
        p = self.sudo()
        state = dict(p._fields["state"]._description_selection(self.env)).get(p.state)
        head = f"⚙️{p.name}"
        desc = f"{p.state_symbol}{state}"
        return head, desc
