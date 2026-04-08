# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022


from odoo import models


class ResUsers(models.Model):
    _inherit = "res.users"

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """Extend writeable fields so users can edit their own
        auto-subscribe settings.
        """
        return super().SELF_WRITEABLE_FIELDS + [
            "auto_subscribe_on_tag",
            "auto_subscribe_on_message",
            "auto_subscribe_on_activity",
        ]
