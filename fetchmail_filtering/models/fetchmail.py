# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

import logging

from odoo import api, models, _
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class FetchmailServer(models.AbstractModel):
    _inherit = 'fetchmail.server'

    @api.model
    @ormcache()
    def _get_db_fetchmail_allowedlist(self):
        res = []
        allowedlist = config.get("db_fetchmail_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def _fetch_mails(self):
        if self.env.cr.dbname in self._get_db_fetchmail_allowedlist():
            return super()._fetch_mails()
        else:
            _logger.info('_fetch_mails disabled')
            return None
