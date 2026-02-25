# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import email
import logging

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from odoo import api, models

_logger = logging.getLogger(__name__)

ODOO_MSGID = "-openerp"
LOOP_MSGID = "-loop" + ODOO_MSGID


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _debug_incoming_message(self, message):
        # Use the same logic from odoo/addons/mail/models/mail_thread.py
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode("utf-8")
        message = email.message_from_bytes(message, policy=email.policy.SMTP)
        # compute received headers into one variable
        received = ""
        for header in message._headers:
            if header and len(header) >= 2 and header[0].lower() == "received":
                received += "\n" + header[1]
        # print result
        data = {
            "Message-Id": repr(message.get("Message-Id")),
            "References": message.get("References", ""),
            "In-Reply-To": message.get("In-Reply-To", ""),
            "Return-Path": message.get("Return-Path", ""),
            "Reply-To": message.get("Reply-To", ""),
            "Date": message.get("Date", ""),
            "From": message.get("From", ""),
            "To": message.get("To"),
            "Cc": message.get("Cc", ""),
            "Bcc": message.get("Bcc", ""),
            "Subject": message.get("Subject", ""),
            "Received": received,
        }
        # remove empty values
        data = {k: v for k, v in data.items() if v}
        width = max(len(k) for k in data)
        details = "\n".join(f"{k:>{width}}: {v}" for k, v in data.items())
        _logger.info("📨 Incoming E-Mail\n%s\n", details)

    def message_process(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        strip_attachments=False,
        thread_id=None,
    ):
        self._debug_incoming_message(message)
        thread_id = super().message_process(
            model=model,
            message=message,
            custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments,
            thread_id=thread_id,
        )
        return thread_id
