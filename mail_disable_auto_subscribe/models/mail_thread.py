# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def message_subscribe(self, partner_ids=None, subtype_ids=None):
        """Override to tag manual subscriptions with a context key.
        This allows subtype filtering to distinguish between auto and manual
        subscriptions.
        """
        _self = self
        if (
            "mail_post_autofollow" not in _self.env.context
            and "mail_activity_autofollow" not in _self.env.context
        ):
            _self = _self.with_context(manual_message_subscribe=True)
        return super(MailThread, _self).message_subscribe(
            partner_ids=partner_ids,
            subtype_ids=subtype_ids,
        )

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        """Override to filter auto-subscribed partners based on their preferences.
        Partners with auto_subscribe_on_tag=False are filtered out when the
        subscription is triggered by a mail post with autofollow enabled.
        Partners with auto_subscribe_on_activity=False are filtered out when the
        subscription is triggered by an activity assignment.
        """
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
        return super()._message_subscribe(
            partner_ids=partner_ids,
            subtype_ids=subtype_ids,
            customer_ids=customer_ids,
        )

    def message_post(self, **kwargs):
        """Override to prevent author auto-subscribe when they opted out.
        When the posting user or the explicit author has auto_subscribe_on_message
        set to False, mail_create_nosubscribe is injected into the context so
        the base message_post does not subscribe them as a follower.
        """
        _self = self
        # determine the effective author that would be auto-subscribed
        if self.env.user.active:
            real_author = self.env.user.partner_id
        else:
            author_id = kwargs.get("author_id")
            real_author = (
                self.env["res.partner"].browse(author_id) if author_id else None
            )
        if real_author and not real_author.auto_subscribe_on_message:
            _self = _self.with_context(mail_create_nosubscribe=True)
        return super(MailThread, _self).message_post(**kwargs)
