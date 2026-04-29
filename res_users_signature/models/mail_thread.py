# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_by_email_prepare_rendering_context(
        self,
        message,
        msg_vals=False,
        model_description=False,
        force_email_company=False,
        force_email_lang=False,
    ):
        """Override to replace the full signature with the shorter answer signature."""
        res = super()._notify_by_email_prepare_rendering_context(
            message,
            msg_vals=msg_vals,
            model_description=model_description,
            force_email_company=force_email_company,
            force_email_lang=force_email_lang,
        )
        if res.get("signature") and message.email_add_signature:
            if message.author_id and message.author_id.user_ids:
                user = message.author_id.user_ids[0]
                if message.email_add_signature and user.signature_answer:
                    if message.subtype_id.internal:
                        _logger.info("replacing 'signature' with a shorter one #1")
                        res["signature"] = user.signature_answer
                    elif message.subject:
                        if "Re:" in message.subject or "Re :" in message.subject:
                            _logger.info("replacing 'signature' with a shorter one #2")
                            res["signature"] = user.signature_answer
        return res
