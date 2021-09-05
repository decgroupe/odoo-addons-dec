# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

import logging

from odoo import api, models, _
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class GoogleCalendar(models.AbstractModel):
    STR_SERVICE = 'calendar'
    _inherit = 'google.%s' % STR_SERVICE

    @api.model
    @ormcache()
    def _get_db_googlesync_allowedlist(self):
        res = []
        allowedlist = config.get("db_googlesync_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def synchronize_events_cron(self):
        if self.env.cr.dbname in self._get_db_googlesync_allowedlist():
            return super().synchronize_events_cron()
        else:
            _logger.info('synchronize_events_cron disabled')
            return None

    def synchronize_events(self, lastSync=True):
        if self.env.cr.dbname in self._get_db_googlesync_allowedlist():
            return super().synchronize_events(lastSync)
        else:
            _logger.info('synchronize_events disabled')
            return {
                "status": "no_new_event_from_google",
                "url": ''
            }
