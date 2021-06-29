# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jun 2021

import logging

from odoo import api, models, _, fields

_logger = logging.getLogger(__name__)


class MailChannel(models.AbstractModel):
    _inherit = 'mail.channel'

    hide_from_slot_list = fields.Boolean(string="Hide from channel list")

    @api.model
    def channel_fetch_slot(self):
        values = super(MailChannel, self).channel_fetch_slot()
        hidden_channels = self.search([
            ('hide_from_slot_list', '=', True),
        ])

        def remove_hidden(list_name):
            values[list_name] = [
                channel_info for channel_info in values[list_name]
                if channel_info['id'] not in hidden_channels.ids
            ]

        remove_hidden('channel_channel')
        remove_hidden('channel_direct_message')
        remove_hidden('channel_private_group')

        return values
