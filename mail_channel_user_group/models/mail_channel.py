# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from odoo import models


class MailChannel(models.AbstractModel):
    _inherit = "mail.channel"

    def _notify_get_groups(self, msg_vals=None):
        """Restore common `group_func` for user group that is removed by our parent
        function"""
        groups = super(MailChannel, self)._notify_get_groups(msg_vals=msg_vals)

        def _in_group_user(recipient):
            if recipient["type"] == "channel_email":
                p = self.env["res.partner"].browse(recipient["id"])
                if all(p.user_ids.mapped(lambda u: u.has_group("base.group_user"))):
                    return True
            return False

        for index, (group_name, group_func, group_data) in enumerate(groups):
            if group_name == "user":
                # hide "See Channel" button for internal users (useless)
                group_data["has_button_access"] = False
                groups[index] = (group_name, _in_group_user, group_data)

        return groups
