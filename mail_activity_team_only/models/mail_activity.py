# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2023


from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("unset_activity_default_user"):
            for vals in vals_list:
                vals["user_id"] = False
        activity_ids = super().create(vals_list)
        return activity_ids
