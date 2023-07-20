# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def action_generate_signatures(self):
        global_template = self.env.ref("res_users_signature.user_signature_template")
        for user in self:
            template = user.signature_template or global_template
            user._generate_from_template(template)

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
        if res.get("signature") and message.subject:
            if "Re:" in message.subject or "Re :" in message.subject:
                if message.author_id and message.author_id.user_ids:
                    user = message.author_id.user_ids[0]
                    if message.add_sign and user.signature_answer:
                        res["signature"] = user.signature_answer
        return res
