# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging


from odoo import api, models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_classify_recipients(self, recipient_data, model_name, msg_vals=None):
        """The purpose of this hook is to make a copy of `recipients` data because this
        value will be dropped (using pop) before template rendering.
        """
        res = super()._notify_classify_recipients(
            recipient_data=recipient_data, model_name=model_name, msg_vals=msg_vals
        )
        for group_data in res:
            recipient_ids = group_data["recipients"]
            group_data["_recipients"] = self.env["res.partner"].browse(recipient_ids)
            group_data["_notif_mode"] = {}
            for r in recipient_data:
                if r["id"] in recipient_ids:
                    group_data["_notif_mode"][r["id"]] = r["notif"]
        return res

    def _notify_record_by_email(
        self,
        message,
        recipients_data,
        msg_vals=False,
        model_description=False,
        mail_auto_delete=True,
        check_existing=False,
        force_send=True,
        send_after_commit=True,
        **kwargs
    ):
        """Add a list of textual recipients to the template context in order to
        to write who are notified of this message
        """
        partners_data = recipients_data["partners"]
        model = msg_vals.get("model") if msg_vals else message.model
        model_name = model_description or (
            self._fallback_lang().env["ir.model"]._get(model).display_name
            if model
            else False
        )  # one query for display name
        recipients_groups_data = self._notify_classify_recipients(
            partners_data, model_name, msg_vals=msg_vals
        )
        if not msg_vals:
            msg_vals = {}
        msg_vals["recipients_groups_data"] = recipients_groups_data
        return super()._notify_record_by_email(
            message,
            recipients_data,
            msg_vals=msg_vals,
            model_description=model_description,
            mail_auto_delete=mail_auto_delete,
            check_existing=check_existing,
            force_send=force_send,
            send_after_commit=send_after_commit,
            **kwargs
        )

    @api.model
    def _notify_prepare_template_context(
        self, message, msg_vals, model_description=False, mail_auto_delete=True
    ):
        res = super()._notify_prepare_template_context(
            message,
            msg_vals,
            model_description,
            mail_auto_delete,
        )
        res["recipients_groups_data"] = msg_vals["recipients_groups_data"]
        return res
