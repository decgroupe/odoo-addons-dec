# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _notify(
        self,
        message,
        rdata,
        record,
        force_send=False,
        send_after_commit=True,
        model_description=False,
        mail_auto_delete=True,
    ):
        if self.env.context.get("mail_partner_notify_disable") or self.env.context.get(
            "mail_partner_notify_disable_email"
        ):
            _logger.info("📧 E-Mail notification disabled")
            return True
        else:
            return super(ResPartner, self)._notify(
                message,
                rdata=rdata,
                record=record,
                force_send=force_send,
                send_after_commit=send_after_commit,
                model_description=model_description,
                mail_auto_delete=mail_auto_delete,
            )

    def _notify_by_chat(self, message):
        if self.env.context.get("mail_partner_notify_disable") or self.env.context.get(
            "mail_partner_notify_disable_chat"
        ):
            _logger.info("💬 Chat notification disabled")
            return
        else:
            return super()._notify_by_chat(message)
