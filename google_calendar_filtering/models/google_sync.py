# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

import logging

from odoo import api, models
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

from odoo.addons.google_account.models.google_service import TIMEOUT
from odoo.addons.google_calendar.utils.google_calendar import GoogleCalendarService
from odoo.addons.google_calendar.utils.google_event import GoogleEvent

_logger = logging.getLogger(__name__)


class GoogleSync(models.AbstractModel):
    _inherit = "google.calendar.sync"

    @api.model
    @ormcache()
    def _get_db_allowedlist(self):
        """Return the list of databases allowed to sync with Google Calendar.
        The list is read from the `db_googlesync_allowedlist` config parameter.
        """
        res = []
        allowedlist = config.get("db_googlesync_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    def _sync_odoo2google(self, google_service: GoogleCalendarService):
        """Sync records to Google only if the current database is allowed."""
        if self.env.cr.dbname in self._get_db_allowedlist():
            return super()._sync_odoo2google(google_service)
        else:
            _logger.info("_sync_odoo2google disabled")
            return None

    @api.model
    def _sync_google2odoo(
        self, google_events: GoogleEvent, write_dates=None, default_reminders=()
    ):
        """Sync records from Google only if the current database is allowed."""
        if self.env.cr.dbname in self._get_db_allowedlist():
            return super()._sync_google2odoo(
                google_events, write_dates, default_reminders
            )
        else:
            _logger.info("_sync_google2odoo disabled")
            return None

    def _google_insert(
        self, google_service: GoogleCalendarService, values, timeout=TIMEOUT
    ):
        """Insert record into Google only if the current database is allowed."""
        if self.env.cr.dbname in self._get_db_allowedlist():
            return super()._google_insert(google_service, values, timeout)
        else:
            _logger.info("_google_insert disabled")
            return None
