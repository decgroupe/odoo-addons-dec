# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import api, fields, models

PRODUCTION_STATE_SYMBOLS = {
    "draft": "✨",
    "confirmed": "🏳️",
    "planned": "📅",  # FIXME: state removed from Odoo 18.0
    "progress": "🚧",
    "done": "✅",
    "to_close": "🛑",
    "cancel": "❌",
}


class Production(models.Model):
    _inherit = "mrp.production"

    state_symbol = fields.Char(compute="_compute_state_symbol")

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = PRODUCTION_STATE_SYMBOLS.get(rec.state, "")

    def get_head_state_code_symbol(self):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        code = self.state
        symbol = self.state_symbol
        return state, code, symbol

    def get_head_desc(self):
        state, _code, symbol = self.get_head_state_code_symbol()
        head = f"🔧{self.name}"
        desc = f"{symbol}{state}"
        return head, desc

    def write(self, vals):
        if "move_dest_ids" in vals:
            for move in self.move_dest_ids:
                move._archive_created_productions()
        return super().write(vals)
