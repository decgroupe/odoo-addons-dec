# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def map_user_partner_to_calendar_event(self):
        users = self.with_context(active_test=False).search([])
        for user_id in users:
            user_events = self.env['calendar.event'].search(
                [
                    ('user_id', '=', user_id.id),
                    ('partner_ids', '=', False),
                ]
            )
            if user_id.partner_id:
                _logger.info(
                    'Adding participant %s to %d events',
                    user_id.partner_id.display_name, len(user_events)
                )
                user_events.write({
                    'partner_ids': [(6, 0, [user_id.partner_id.id])],
                })
            else:
                _logger.info(
                    '!!! No partner linked to %s %s', user_id.display_name,
                    user_id
                )
