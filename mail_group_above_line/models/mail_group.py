# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026


from odoo import api, models


class MailGroup(models.Model):
    _inherit = "mail.group"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, message_type="notification", **kwargs):
        """When an email is fetched the `_message_route_process` will run `message_post`
        on the matching record if a reference if found.
        """
        if "body" in kwargs:
            kwargs["body"] = self.env[
                "mail.thread"
            ]._remove_everything_except_above_this_line(kwargs["body"])
        return super().message_post(message_type=message_type, **kwargs)
