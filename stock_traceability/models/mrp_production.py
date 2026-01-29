# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

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

    def get_head_desc(self):
        # Soft dependency to `mrp_stage` module
        if hasattr(self, "stage_id"):
            state = self.stage_id.name
            code = self.stage_id.code
            symbol = self.stage_id.symbol
        else:
            state = dict(self._fields["state"]._description_selection(self.env)).get(
                self.state
            )
            code = self.state
            symbol = self.state_symbol

        # Soft dependency to `mrp_timesheet` module
        if hasattr(self, "progress") and code == "progress":
            state = f"{state} {self.progress:.0f}%"
        # Soft dependency to `mrp_supply_progress` module
        elif hasattr(self, "supply_progress") and code == "supplying":
            state = f"{state} {self.supply_progress:.0f}%"

        head = f"🔧{self.name}"
        desc = f"{symbol}{state}"
        return head, desc
