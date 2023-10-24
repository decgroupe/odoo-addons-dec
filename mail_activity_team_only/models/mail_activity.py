# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023


from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model
    def create(self, values):
        if self.env.context.get("unset_activity_default_user"):
            values["user_id"] = False
        activity = super(MailActivity, self).create(values)
        return activity
