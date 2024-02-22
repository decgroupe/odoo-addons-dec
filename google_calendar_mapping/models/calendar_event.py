# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2024

from odoo import api, models, tools, _


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    @api.model
    def _odoo_attendee_commands(self, google_event):
        """Hook `google_event` data before being processed by `google_calendar` module"""
        # replace in-place emails (google email => odoo email)
        for attendee in google_event.attendees:
            attendee_email = tools.email_normalize(attendee.get("email"))
            user_id = self.env["res.users"].search(
                [("google_calendar_cal_id", "=", attendee_email)], limit=1
            )
            if user_id:
                attendee["email"] = user_id.email
        attendee_commands, partner_commands = super()._odoo_attendee_commands(
            google_event
        )
        return attendee_commands, partner_commands

    def _google_values(self):
        """Replace values prepared by odoo  before being sent to google"""

        def replace_email(item, user_id):
            if item and user_id and user_id.google_calendar_cal_id:
                email = item.get("email")
                if email and email != user_id.google_calendar_cal_id:
                    item["email"] = user_id.google_calendar_cal_id

        values = super()._google_values()
        # replace organizer email (odoo email => google email)
        organizer = values.get("organizer")
        if organizer:
            replace_email(organizer, self.user_id)
        # replace attendees email (odoo email => google email)
        attendees = values.get("attendees")
        for attendee in attendees:
            user_id = self.env["res.users"].search(
                [("email", "=", attendee.get("email"))], limit=1
            )
            replace_email(attendee, user_id)
        return values
