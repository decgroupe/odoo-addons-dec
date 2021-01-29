# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def _link_to_business_exception(self, business_exception):
        """ Keep only some references to activities redirected by this
            `business_exception`.
        """
        history_activity_ids = self.env['mail.activity']
        if business_exception and self:
            history_activity_ids = self
            existing_activity_ids = business_exception.activity_ids.sorted(
                key=lambda r: r.id, reverse=True
            )
            for existing_activity_id in existing_activity_ids:
                if len(history_activity_ids) >= 5:
                    break
                history_activity_ids += existing_activity_id
            business_exception.activity_ids = history_activity_ids

