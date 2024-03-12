# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2022

import logging

from odoo import _, api, models
from odoo.addons.google_calendar.utils.google_calendar import GoogleCalendarService

_logger = logging.getLogger(__name__)


class User(models.Model):
    _inherit = "res.users"

    def _sync_google_calendar(self, calendar_service: GoogleCalendarService):
        allowed = self.env["google.calendar.sync"]._get_db_allowedlist()
        if self.env.cr.dbname in allowed:
            return super()._sync_google_calendar(calendar_service)
        else:
            _logger.info("_sync_google_calendar disabled")
            return None

    @api.model
    def _sync_all_google_calendar(self):
        allowed = self.env["google.calendar.sync"]._get_db_allowedlist()
        if self.env.cr.dbname in allowed:
            return super()._sync_all_google_calendar()
        else:
            _logger.info("_sync_all_google_calendar disabled")
            return None

    def sync_google_calendar(self):
        google = GoogleCalendarService(self.env['google.service'])
        for user in self:
            if user.google_calendar_rtoken:
                user.with_user(user).sudo()._sync_google_calendar(google)
