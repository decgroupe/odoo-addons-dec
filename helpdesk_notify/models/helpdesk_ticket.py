# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if self._should_notify_new_ticket():
            rec._notify_new_ticket(
                team_id=self.env["helpdesk.ticket.team"].browse(vals.get("team_id")),
                assigned_user_id=self.env["res.users"].browse(vals.get("user_id")),
            )
        return rec

    def _notify_new_ticket(self, team_id, assigned_user_id):
        self.ensure_one()
        if team_id:
            # Check if assigned_user_id is set and is in this team otherwise
            # send an e-mail to all members of this team
            if not assigned_user_id or (assigned_user_id not in team_id.user_ids):
                emails = []
                for user_id in team_id.user_ids:
                    emails.append(user_id.partner_id.email)
                    # self.message_subscribe(
                    #     partner_ids=user_id.partner_id.ids
                    # )
                self.with_context(emails=",".join(emails)).send_user_internal_mail()

    def send_user_internal_mail(self):
        self.env.ref("helpdesk_notify.created_ticket_internal_template").send_mail(
            self.id, force_send=True
        )

    def _should_notify_new_ticket(self):
        return self.env.context.get("fetchmail_cron_running", False)
