# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    @api.model
    def _debug_outgoing_message(self, message):
        data = {
            "Message-Id": repr(message.get("Message-Id")),
            "Return-Path": message.get("Return-Path"),
            "Reply-To": message.get("Reply-To"),
            "From": message.get("From"),
            "To": message.get("To"),
            "Cc": message.get("Cc"),
            "Bcc": message.get("Bcc"),
            "Subject": message.get("Subject"),
        }
        # remove empty values
        data = {k: v for k, v in data.items() if v}
        width = max(len(k) for k in data)
        details = "\n".join(f"{k:>{width}}: {v}" for k, v in data.items())
        _logger.info("📮 Outgoing E-Mail\n%s\n", details)

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
        smtp_ssl_certificate=None,
        smtp_ssl_private_key=None,
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
            smtp_ssl_certificate=smtp_ssl_certificate,
            smtp_ssl_private_key=smtp_ssl_private_key,
            smtp_debug=smtp_debug,
            smtp_session=smtp_session,
        )
        return message_id
