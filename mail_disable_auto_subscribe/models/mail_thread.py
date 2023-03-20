# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def message_subscribe(self, partner_ids=None, channel_ids=None, subtype_ids=None):
        _self = self
        if (
            "mail_post_autofollow" not in _self.env.context
            and "mail_activity_autofollow" not in _self.env.context
        ):
            _self = _self.with_context(manual_message_subscribe=True)
        return super(MailThread, _self)._message_subscribe(
            partner_ids=partner_ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids,
        )

    def _message_subscribe(
        self, partner_ids=None, channel_ids=None, subtype_ids=None, customer_ids=None
    ):
        if self.env.context.get("mail_post_autofollow") and partner_ids:
            partner_ids = (
                self.env["res.partner"]
                .browse(partner_ids)
                .filtered("auto_subscribe_on_tag")
                .ids
            )
        if self.env.context.get("mail_activity_autofollow") and partner_ids:
            partner_ids = (
                self.env["res.partner"]
                .browse(partner_ids)
                .filtered("auto_subscribe_on_activity")
                .ids
            )
        return super(MailThread, self)._message_subscribe(
            partner_ids=partner_ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids,
            customer_ids=customer_ids,
        )

    def _message_post_after_hook(
        self,
        message,
        msg_vals,
    ):
        if msg_vals["author_id"] and msg_vals["model"] and self.ids:
            partner_id = self.env["res.partner"].browse(msg_vals["author_id"])
            if partner_id and not partner_id.auto_subscribe_on_message:
                self = self.with_context(mail_create_nosubscribe=True)

        return super(MailThread, self)._message_post_after_hook(message, msg_vals)

    # TODO: [MIG] 14.0: Check if this hook is still necessary
    def _notify_classify_recipients(self, recipient_data, model_name, msg_vals=None):
        """This hook is made to convert internal user/partner recipient to
        type `user` because when odoo convert channel to partners in
        `_notify_recipients`, they are all set with default type
        `customer`.
        That way, the « See » Action will be available.

        """
        is_internal = lambda p: (
            p.user_ids
            and all(p.user_ids.mapped(lambda u: u.has_group("base.group_user")))
        )
        for recipient in recipient_data:
            partner_id = self.env["res.partner"].browse(recipient["id"])
            if is_internal(partner_id):
                recipient["type"] = "user"
        return super()._notify_classify_recipients(
            recipient_data=recipient_data, model_name=model_name, msg_vals=msg_vals
        )
