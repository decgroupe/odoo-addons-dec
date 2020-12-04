# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Dec 2020

import logging

from odoo import api, models, _
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)


class MailMail(models.AbstractModel):
    _inherit = 'mail.mail'

    @api.model
    @ormcache()
    def _get_db_process_email_allowedlist(self):
        res = []
        allowedlist = config.get("db_process_email_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def process_email_queue(self, ids=None):
        if self.env.cr.dbname in self._get_db_process_email_allowedlist():
            return super().process_email_queue(ids)
        else:
            _logger.info('process_email_queue disabled')
            return None

    @api.multi
    def _send(
        self,
        auto_commit=False,
        raise_exception=False,
        smtp_session=None,
    ):
        if self.env.cr.dbname in self._get_db_process_email_allowedlist():
            return super()._send(
                auto_commit, raise_exception, smtp_session
            )
        else:
            _logger.info('_send disabled')
            return False
