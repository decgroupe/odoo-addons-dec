# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class MailMessage(models.AbstractModel):
    _inherit = "mail.message"

    def _ensure_create_values(self, vals_list):
        """When filling default values, upstream will check for existing key in values
        dictionary, but don't care if this value exists and is False. The purpose of
        this function is to delete False values from the dictionary to ensure valid
        default values will be filled by ./odoo/addons/mail/models/mail_message.py
        """
        for values in vals_list:
            if "email_from" in values and not values["email_from"]:
                values.pop("email_from")
                _logger.info("Empty field 'email_from' dropped")
            if "reply_to" in values and not values["reply_to"]:
                values.pop("reply_to")
                _logger.info("Empty field 'reply_to' dropped")

    @api.model_create_multi
    def create(self, vals_list):
        self._ensure_create_values(vals_list)
        return super().create(vals_list)
