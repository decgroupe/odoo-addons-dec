# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

import logging
import re

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

PATTERN = r'<img src=".*\/mail\/tracking\/open\/([^\/]*)\/([^\/]*)\/([^\/]*)\/blank\.gif'


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def _message_route_get_thread_references(self, message, message_dict):
        res = super()._message_route_get_thread_references(
            message, message_dict
        )
        if not res:
            message_id = self._get_message_id_from_tracking_data(message_dict)
            if message_id:
                res = message_id
        return res

    @api.model
    def _get_message_id_from_tracking_data(self, message_dict):
        res = False
        matches = re.search(PATTERN, message_dict.get('body'), re.MULTILINE)
        if matches and len(matches.groups()) == 3:
            db = matches.group(1)
            tracking_email_id = matches.group(2)
            token = matches.group(3)

            if self.env.cr.dbname == db:
                tracking_email = self.env['mail.tracking.email'].search(
                    [
                        ('id', '=', tracking_email_id),
                        ('token', '=', token),
                    ]
                )
                res = tracking_email.mail_message_id.message_id
        return res
