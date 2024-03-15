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
        _logger.info(
            "📨 Incoming E-Mail\n"
            "   Message-Id: %r\n"
            "   References: %s\n"
            "  In-Reply-To: %s\n"
            "  Return-Path: %s\n"
            "     Reply-To: %s\n"
            "         Date: %s\n"
            "         From: %s\n"
            "           To: %s\n"
            "           Cc: %s\n"
            "          Bcc: %s\n"
            "      Subject: %s\n"
            "     Received: %s\n",
            message.get("Message-Id"),
            message.get("References", ""),
            message.get("In-Reply-To", ""),
            message.get("Return-Path", ""),
            message.get("Reply-To", ""),
            message.get("Date", ""),
            message.get("From", ""),
            message.get("To"),
            message.get("Cc", ""),
            message.get("Bcc", ""),
            message.get("Subject", ""),
            received,
        )

    def _message_process_duplicated_messages(self, message):
        """Rename incoming e-mail sent by our system in order to process their route
        correctly (duplicated Message-Id are ignored by Odoo while processing).
        It is necessary when a mail is sent to a channel from odoo.
        A security is added to avoid processing a duplicate more than once.
        """
        # Use the same logic from odoo/addons/mail/models/mail_thread.py
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode("utf-8")
        email_message = email.message_from_bytes(message, policy=email.policy.SMTP)
        message_id = email_message["message-id"]
        if message_id and ODOO_MSGID in message_id:
            # checks if Message-Id is already in the database
            existing_message_ids = self.env["mail.message"].search(
                [("message_id", "=", message_id)],
            )
            if existing_message_ids:
                if LOOP_MSGID in message_id:
                    _logger.info(
                        "🧽 Duplicated incoming e-mail with Message-Id %s "
                        "already processed.",
                        message_id,
                    )
                else:
                    del email_message["message-id"]
                    email_message["message-id"] = message_id.replace(
                        ODOO_MSGID, LOOP_MSGID
                    )
                    _logger.info(
                        "🧽 Duplicated incoming e-mail with Message-Id %s "
                        "renamed to Message-Id %s",
                        message_id,
                        email_message["message-id"],
                    )
                    # reconvert EmailMessage object to bytes (original format)
                    message = bytes(email_message)
        return message

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
        message = self._message_process_duplicated_messages(message)
        thread_id = super().message_process(
            model=model,
            message=message,
            custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments,
            thread_id=thread_id,
        )
        return thread_id