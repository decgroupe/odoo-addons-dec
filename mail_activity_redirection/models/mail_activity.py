# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    @api.multi
    def _link_to_mail_activity_redirection(self, mail_activity_redirection):
        """ Keep only some references to activities redirected by this
            `mail_activity_redirection`.
        """
        history_activity_ids = self.env['mail.activity']
        if mail_activity_redirection and self:
            history_activity_ids = self
            existing_activity_ids = mail_activity_redirection.activity_ids.sorted(
                key=lambda r: r.id, reverse=True
            )
            for existing_activity_id in existing_activity_ids:
                if len(history_activity_ids) >= 5:
                    break
                history_activity_ids += existing_activity_id
            # Use sudo since normal user don't have write access
            mail_activity_redirection.sudo().activity_ids = history_activity_ids

