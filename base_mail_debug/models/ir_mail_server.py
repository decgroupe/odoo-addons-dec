# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def _debug_outgoing_message(self, message):
        _logger.info(
            "📮 Outgoing E-Mail\n"
            "   Message-Id: %r\n"
            "  Return-Path: %s\n"
            "     Reply-To: %s\n"
            "         From: %s\n"
            "           To: %s\n"
            "           Cc: %s\n"
            "          Bcc: %s\n"
            "      Subject: %s\n",
            message.get("Message-Id"),
            message.get("Return-Path"),
            message.get("Reply-To"),
            message.get("From"),
            message.get("To"),
            message.get("Cc"),
            message.get("Bcc"),
            message.get("Subject"),
        )

    @api.model
    def send_email(
        self,
        message,
        mail_server_id=None,
        smtp_server=None,
        smtp_port=None,
        smtp_user=None,
        smtp_password=None,
        smtp_encryption=None,
        smtp_debug=False,
        smtp_session=None,
    ):
        self._debug_outgoing_message(message)
        message_id = super().send_email(
            message,
            mail_server_id=mail_server_id,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password,
            smtp_encryption=smtp_encryption,
            smtp_debug=smtp_debug,
            smtp_session=smtp_session,
        )
        return message_id
