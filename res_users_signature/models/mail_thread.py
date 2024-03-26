# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging


from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def _notify_prepare_template_context(
        self, message, record, model_description=False, mail_auto_delete=True
    ):
        res = super()._notify_prepare_template_context(
            message,
            record,
            model_description,
            mail_auto_delete,
        )
        if res.get("signature") and message.add_sign:
            if message.author_id and message.author_id.user_ids:
                user = message.author_id.user_ids[0]
                if message.add_sign and user.signature_answer:
                    if message.subtype_id.internal:
                        res["signature"] = user.signature_answer
                    elif message.subject:
                        if "Re:" in message.subject or "Re :" in message.subject:
                            res["signature"] = user.signature_answer
        return res
