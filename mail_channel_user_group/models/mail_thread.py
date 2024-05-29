# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def _notify_compute_recipients(self, message, msg_vals):
        """When partner data is generated from a channel, groups are not added.
        The purpose of this overrides is to re-add them
        """
        recipient_data = super()._notify_compute_recipients(message, msg_vals)
        for pdata in recipient_data["partners"]:
            if pdata["type"] == "channel_email":
                p = self.env["res.partner"].browse(pdata["id"])
                pdata["groups"] = p.user_ids.groups_id.ids
        return recipient_data

    def _notify_get_groups(self, msg_vals=None):
        """Create a new group that include internal users notified by a channel (that
        means when a channel is tagged using #channel_name in the chatter).
        Otherwise everyone is considered a customer (no action).
        Note that this group will be overriden by Odoo in base "mail.channel" and
        that explains why there is an another override in
        `mail_channel_user_group/models/mail_channel.py`
        """
        groups = super(MailThread, self)._notify_get_groups(msg_vals=msg_vals)

        def _user_in_group_channel_email(recipient):
            _logger.debug("_user_in_group_channel_email")
            if recipient["type"] == "channel_email":
                if self.env.ref("base.group_user").id in recipient["groups"]:
                    return True
            return False

        actions = []
        new_group = (
            "group_channel_email",
            _user_in_group_channel_email,
            {"actions": actions},
        )
        # insert the new `group_channel_email` just after the `user` group.
        # the purpose of this step is to avoid interaction with newly added groups
        # from other addons.
        for i, (group_name, _group_func, _group_data) in enumerate(groups):
            if group_name == "user":
                groups.insert(i + 1, new_group)
                break
        return groups

    def _notify_classify_recipients(self, recipient_data, model_name, msg_vals=None):
        """Since a user added to the `group_channel_email` is an internal user, we
        check if it could be moved to the `user` group instead. To do so, we use the
        original lambda function from the `user` group to validate the move.
        """
        local_msg_vals = dict(msg_vals) if msg_vals else {}
        group_user_func = False
        group_channel_email_func = False
        for group in self._notify_get_groups(msg_vals=local_msg_vals):
            group_name, group_func, _group_data = group
            if group_name == "user":
                group_user_func = group_func
            if group_name == "group_channel_email":
                group_channel_email_func = group_func
        # browse recipients to see if they need to be moved to another type
        if group_user_func and group_channel_email_func:
            for recipient in recipient_data:
                if group_channel_email_func(recipient):
                    # make a copy to not edit original content
                    recipient_copy = recipient.copy()
                    recipient_copy["type"] = "user"
                    if group_user_func(recipient_copy):
                        # this recipient is accepted by the user group, we can
                        # now replace original data
                        recipient["type"] = "user"
        return super()._notify_classify_recipients(
            recipient_data=recipient_data, model_name=model_name, msg_vals=msg_vals
        )
