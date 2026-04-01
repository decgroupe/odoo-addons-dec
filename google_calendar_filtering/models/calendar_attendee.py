# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo import models

from odoo.addons.calendar.models.calendar_attendee import Attendee as AttendeeBase


class Attendee(models.Model):
    _name = "calendar.attendee"
    _inherit = "calendar.attendee"

    def _send_mail_to_attendees(self, mail_template, force_send=False):
        """Send mail for event invitation to event attendees.
        If the current database is in the allowed list, delegate to the full
        MRO chain (including google_calendar overrides). Otherwise, bypass
        any google_calendar hook and call the base calendar implementation
        directly.
        """
        if self.env.cr.dbname in self.event_id._get_db_allowedlist():
            return super()._send_mail_to_attendees(mail_template, force_send)
        else:
            return AttendeeBase._send_mail_to_attendees(self, mail_template, force_send)
