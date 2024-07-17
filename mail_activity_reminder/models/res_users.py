# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2024


import logging
import datetime
import uuid

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = "res.users"

    # for external access
    activity_reminder_access_token = fields.Char(
        string="Activity Reminder Access Token",
        groups="base.group_user",
    )

    def _generate_new_activity_reminder_access_token(self):
        return str(uuid.uuid4())

    def generate_new_activity_reminder_access_token(self):
        for user in self:
            user.activity_reminder_access_token = (
                user._generate_new_activity_reminder_access_token()
            )

    def _get_reminder_base_domain(self):
        self.ensure_one()
        return [
            "|",
            ("user_id", "=", self.id),
            "&",
            ("team_id.member_ids", "=", self.id),
            ("user_id", "=", False),
        ]

    def _get_group_activity_ids(self, domain_extra):
        self.ensure_one()
        domain = self._get_reminder_base_domain()
        domain += domain_extra
        activity_ids = self.env["mail.activity"].search(
            domain, order="date_deadline desc"
        )
        group_activity_ids = {
            activity_type_id: []
            for activity_type_id in activity_ids.mapped("activity_type_id")
        }
        for activity_id in activity_ids:
            group_activity_ids[activity_id.activity_type_id].append(activity_id)
        return group_activity_ids

    def send_activity_reminder(self):
        template_id = self.env.ref(
            "mail_activity_reminder.email_template_activity_reminder"
        )
        #  + datetime.timedelta(days=30)
        self.generate_new_activity_reminder_access_token()
        for user in self:
            group_late_activity_ids = user._get_group_activity_ids(
                [("date_deadline", "<", fields.Date.context_today(self))]
            )
            group_next_activity_ids = user._get_group_activity_ids(
                [("date_deadline", ">=", fields.Date.context_today(self))]
            )
            # domain = user._get_reminder_base_domain()
            # domain.append()
            # activity_ids = self.env["mail.activity"].search(
            #     domain, order="date_deadline desc"
            # )

            # group_activity_ids = {
            #     activity_type_id: []
            #     for activity_type_id in activity_ids.mapped("activity_type_id")
            # }
            # for activity_id in activity_ids:
            #     group_activity_ids[activity_id.activity_type_id].append(activity_id)

            ctx = {
                "token": user.activity_reminder_access_token,
                "group_late_activity_ids": group_late_activity_ids,
                "group_next_activity_ids": group_next_activity_ids,
            }

            template_id.with_context(**ctx).send_mail(
                self.id,
                force_send=True,
                email_values={"email_to": user.email_formatted},
            )
