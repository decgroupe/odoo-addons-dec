# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from odoo import models


class DiscussChannel(models.Model):
    _inherit = "discuss.channel"

    def _notify_get_recipients_groups(self, message, model_description, msg_vals=None):
        """Restore user group classification for internal users notified via a channel.
        In Odoo 18.0, discuss.channel forces all non-customer groups to a no-match
        lambda, making every recipient fall into the customer group. We restore the
        user group for internal users while keeping the 'See Channel' button hidden
        since it is irrelevant for channel messages.
        """
        groups = super()._notify_get_recipients_groups(
            message, model_description, msg_vals=msg_vals
        )
        for index, (group_name, _group_func, group_data) in enumerate(groups):
            if group_name == "user":
                # restore real user-group matching for internal users, but hide
                # the 'see channel' button since it is not useful in this context
                group_data["has_button_access"] = False
                groups[index] = (
                    group_name,
                    lambda pdata: pdata["type"] == "user",
                    group_data,
                )
        return groups
