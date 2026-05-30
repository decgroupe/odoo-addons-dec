# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestMailActivityScheduleCommon(TransactionCase):
    """Common fixtures for mail_activity_schedule tests."""

    @classmethod
    def setUpClass(cls):
        """Set up models, views and reusable records for tests."""
        super().setUpClass()
        cls.MailActivity = cls.env["mail.activity"]
        cls.CalendarEvent = cls.env["calendar.event"]
        cls.MailActivityType = cls.env["mail.activity.type"]
        cls.ResModel = cls.env["ir.model"]
        cls.mail_activity_form_popup_view = cls.env.ref(
            "mail.mail_activity_view_form_popup"
        )
        cls.mail_activity_tree_view = cls.env.ref("mail.mail_activity_view_tree")
        cls.mail_activity_type_form_view = cls.env.ref(
            "mail.mail_activity_type_view_form"
        )
        cls.schedule_activity_type = cls.env.ref(
            "mail_activity_schedule.mail_activity_schedule"
        )
        cls.res_partner_model = cls.ResModel._get("res.partner")
        cls.user_partner = cls.env.user.partner_id

    def _create_activity_with_event(self):
        """Create a mail activity linked to a calendar event."""
        start_value = "2026-05-30 08:00:00"
        stop_value = "2026-05-30 10:00:00"
        event = self.CalendarEvent.create(
            {
                "name": "Mail Activity Schedule Test",
                "start": start_value,
                "stop": stop_value,
                "partner_ids": [Command.link(self.user_partner.id)],
            }
        )
        activity = self.MailActivity.create(
            {
                "res_model_id": self.res_partner_model.id,
                "res_id": self.user_partner.id,
                "activity_type_id": self.schedule_activity_type.id,
                "summary": "Sync with calendar",
                "user_id": self.env.user.id,
                "date_deadline": fields.Date.today(),
                "date_start": start_value,
                "date_stop": stop_value,
                "calendar_event_id": event.id,
            }
        )
        return activity, event
