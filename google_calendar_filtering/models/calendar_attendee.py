# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo import models

from odoo.addons.calendar.models.calendar_attendee import Attendee as AttendeeBase


class Attendee(models.Model):
    _name = "calendar.attendee"
    _inherit = "calendar.attendee"

    def _send_mail_to_attendees(
        self, template_xmlid, force_send=False, ignore_recurrence=False
    ):
        if self.env.cr.dbname in self.event_id._get_db_allowedlist():
            return super()._send_mail_to_attendees(
                template_xmlid, force_send, ignore_recurrence
            )
        else:
            return AttendeeBase._send_mail_to_attendees(
                self, template_xmlid, force_send, ignore_recurrence
            )
