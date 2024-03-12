# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2021

import email
import logging

try:
    from xmlrpc import client as xmlrpclib
except ImportError:
    import xmlrpclib

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _message_process_delete_duplicated_messages(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        thread_id=None,
    ):
        """Deleting mails, scheduled to be deleted, with duplicated
        Message-Id before processing, otherwise they will be ignored.
        It is necessary when a mail is sent to a channel from odoo.
        """
        # Use the same logic from odoo/addons/mail/models/mail_thread.py
        if isinstance(message, xmlrpclib.Binary):
            message = bytes(message.data)
        if isinstance(message, str):
            message = message.encode("utf-8")
        msg_txt = email.message_from_bytes(message, policy=email.policy.SMTP)

        msg = self.message_parse(msg_txt, save_original=save_original)
        # Checks if Message-Id is already in the database but tagged to be
        # deleted later (using `delayed_deletion`)
        if msg.get("message_id"):
            existing_mail_ids = self.env["mail.mail"].search(
                [
                    ("message_id", "=", msg.get("message_id")),
                    ("delayed_deletion", "!=", False),
                ]
            )
            if existing_mail_ids:
                try:
                    # Like the super method, find possible routes for the
                    # message. If a ValueError exception is raised then no
                    # route exists and the message will not be re-created, in
                    # that case we don't delete it
                    routes = self.message_route(
                        msg_txt, msg, model, thread_id, custom_values
                    )
                    _logger.info(
                        "Deleting mail, scheduled to be deleted, with "
                        "duplicated Message-Id %s before processing.",
                        msg.get("message_id"),
                    )
                    # Instead of deleting mails, we delete messages (ignoring
                    # notification value of mail object) that will also delete mails
                    # via cascade
                    existing_msg_ids = existing_mail_ids.mapped("mail_message_id")
                    existing_msg_ids.unlink()
                except ValueError:
                    _logger.info(
                        "No route found, keep existing mail with " "Message-Id %s",
                        msg.get("message_id"),
                    )

    def message_process(
        self,
        model,
        message,
        custom_values=None,
        save_original=False,
        strip_attachments=False,
        thread_id=None,
    ):
        self._message_process_delete_duplicated_messages(
            model, message, custom_values, save_original, thread_id
        )
        thread_id = super().message_process(
            model=model,
            message=message,
            custom_values=custom_values,
            save_original=save_original,
            strip_attachments=strip_attachments,
            thread_id=thread_id,
        )
        return thread_id
