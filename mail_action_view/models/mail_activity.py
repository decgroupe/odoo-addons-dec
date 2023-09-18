# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def action_view_base(self):
        # Alternative of `mail.mail_activity_action`
        action = {
            "type": "ir.actions.act_window",
            "name": "My Action Name",
            "display_name": "Activities",
            "res_model": "mail.activity",
            "context": "{}",
            "domain": "[]",
            "filter": False,
            "target": "current",
            "view_mode": "form",
            "view_type": "form",
        }
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("mail.mail_activity_view_form_popup")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.ids[0]
        return action
