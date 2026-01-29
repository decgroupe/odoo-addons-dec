# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import api, fields, models
from odoo.tools import html2plaintext

ACTIVITY_STATE_SYMBOLS = {
    "overdue": "🕸️",
    "today": "✅",
    "planned": "📅",
    "done": "✔️",
}


class MailActivity(models.Model):
    _inherit = "mail.activity"

    state_symbol = fields.Char(compute="_compute_state_symbol")

    @api.depends("state")
    def _compute_state_symbol(self):
        for rec in self:
            rec.state_symbol = ACTIVITY_STATE_SYMBOLS.get(rec.state, "")

    def get_head_desc(self, product_id=False):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        activity_text = html2plaintext(self.note or self.summary)
        if product_id:
            product_name = product_id.product_tmpl_id.display_name
            activity_text = activity_text.replace(product_name, "").strip()
        head = f"⚠️{self.date_deadline.strftime('%d/%m/%y')}:{activity_text}"
        desc = f"{self.state_symbol}{state}"
        return head, desc
