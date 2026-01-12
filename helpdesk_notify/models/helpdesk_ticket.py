# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2020

from odoo import api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model_create_multi
    def create(self, vals_list):
        record_ids = super().create(vals_list)
        if self._should_notify_new_ticket():
            for rec, vals in zip(record_ids, vals_list, strict=True):
                rec._notify_new_ticket(
                    team_id=self.env["helpdesk.ticket.team"].browse(
                        vals.get("team_id")
                    ),
                    assigned_user_id=self.env["res.users"].browse(vals.get("user_id")),
                )
        return record_ids

    def _notify_new_ticket(self, team_id, assigned_user_id):
        self.ensure_one()
        if team_id:
            # Check if assigned_user_id is set and is in this team otherwise
            # send an e-mail to all members of this team
            if not assigned_user_id or (assigned_user_id not in team_id.user_ids):
                emails = []
                for user_id in team_id.user_ids:
                    emails.append(user_id.partner_id.email_formatted)
                self.send_user_internal_mail(emails)

    def send_user_internal_mail(self, emails):
        email_values = {"email_to": ",".join(emails)}
        self.env.ref("helpdesk_notify.created_ticket_internal_template").send_mail(
            self.id,
            force_send=True,
            email_values=email_values,
        )

    def _should_notify_new_ticket(self):
        _should_notify = self.env.context.get("fetchmail_cron_running", False)
        if not _should_notify:
            _should_notify = self.env.context.get("force_helpdesk_notify", False)
        if not _should_notify:
            # require our commit
            # [IMP] helpdesk_mgmt: Help to know if a ticket is created from portal
            _should_notify = self.env.context.get("portal_ticket", False)
        return _should_notify

    def get_access_link(self):
        # _notify_get_action_link is not callable from email template
        return self._notify_get_action_link("view")
