# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import logging

from odoo import api, models, _, fields

_logger = logging.getLogger(__name__)


class MailChannel(models.AbstractModel):
    _inherit = 'mail.channel'

    subject_prefix = fields.Char(string="Subject's Prefix")

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, message_type='notification', **kwargs):
        if self.subject_prefix and 'subject' in kwargs:
            kwargs['subject'] = '%s %s' % (
                self.subject_prefix,
                kwargs['subject'],
            )
        return super().message_post(message_type=message_type, **kwargs)
