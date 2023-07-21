# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models
from odoo.tools import html2plaintext


def activity_state_to_emoji(state):
    res = state
    if res == "overdue":
        res = "🕸️"
    elif res == "today":
        res = "✅"
    elif res == "planned":
        res = "📅"
    return res


class MailActivity(models.Model):
    _inherit = "mail.activity"

    state_emoji = fields.Char(compute="_compute_state_emoji")

    def _compute_state_emoji(self):
        for rec in self:
            rec.state_emoji = activity_state_to_emoji(rec.state)

    def get_head_desc(self, product_id=False):
        state = dict(self._fields["state"]._description_selection(self.env)).get(
            self.state
        )
        activity_text = html2plaintext(self.note or self.summary)
        if product_id:
            product_name = product_id.product_tmpl_id.display_name
            activity_text = activity_text.replace(product_name, "")
        head = "⚠️{0}:{1}".format(
            self.date_deadline.strftime("%d/%m/%y"), activity_text
        )
        desc = "{0}{1}".format(self.state_emoji, state)
        return head, desc
