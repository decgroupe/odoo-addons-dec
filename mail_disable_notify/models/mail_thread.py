# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_thread_by_email(
        self,
        message,
        recipients_data,
        msg_vals=False,
        **kwargs,
    ):
        """Disable email notifications when context flag is set."""
        if self.env.context.get("mail_partner_notify_disable") or self.env.context.get(
            "mail_partner_notify_disable_email"
        ):
            _logger.info("📧 E-Mail notification disabled")
            return
        return super()._notify_thread_by_email(
            message,
            recipients_data,
            msg_vals=msg_vals,
            **kwargs,
        )

    def _notify_thread_by_inbox(
        self,
        message,
        recipients_data,
        msg_vals=False,
        **kwargs,
    ):
        """Disable inbox (chat) notifications when context flag is set."""
        if self.env.context.get("mail_partner_notify_disable") or self.env.context.get(
            "mail_partner_notify_disable_chat"
        ):
            _logger.info("💬 Chat notification disabled")
            return
        return super()._notify_thread_by_inbox(
            message,
            recipients_data,
            msg_vals=msg_vals,
            **kwargs,
        )
