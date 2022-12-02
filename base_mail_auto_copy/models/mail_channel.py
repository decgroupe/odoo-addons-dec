# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import logging

from odoo import api, models, _, fields

_logger = logging.getLogger(__name__)


class MailChannel(models.AbstractModel):
    _inherit = 'mail.channel'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, message_type='notification', **kwargs):
        if 'from' in kwargs:
            self = self.with_context(channel_email_from=kwargs.get('email_from'))
        return super(MailChannel, self).message_post(message_type=message_type, **kwargs)
