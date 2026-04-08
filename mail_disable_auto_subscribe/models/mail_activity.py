# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026


from collections import defaultdict

from odoo import api, models


class MailActivity(models.Model):
    _inherit = "mail.activity"

    @api.model_create_multi
    def create(self, vals_list):
        """Create activities and subscribe assigned users who allow it.
        Prevents the default auto-subscription and manually filters partners
        based on the auto_subscribe_on_activity flag before subscribing.
        """
        # prevent default subscription, handle it manually below
        activities = super(
            MailActivity, self.with_context(mail_activity_noautofollow=True)
        ).create(vals_list)
        # subscribe per user only if they allow activity-based subscription
        for model_name, activity_data in activities._classify_by_model().items():
            per_user = defaultdict(set)
            for activity in activity_data["activities"].filtered(lambda a: a.user_id):
                if activity.user_id.partner_id.auto_subscribe_on_activity:
                    per_user[activity.user_id].add(activity.res_id)
            for user, res_ids in per_user.items():
                self.env[model_name].browse(list(res_ids)).with_context(
                    mail_activity_autofollow=True
                ).message_subscribe(partner_ids=user.sudo().partner_id.ids)
        return activities

    def write(self, vals):
        """Update activities, subscribing only users who allow activity auto-subscribe.
        Prevents the default auto-subscription and manually filters the new
        assigned user based on the auto_subscribe_on_activity flag.
        """
        # capture activities where user_id is about to change before write
        new_user_activities = self.env["mail.activity"]
        if vals.get("user_id"):
            new_user_activities = self.filtered(
                lambda a: a.user_id.id != vals["user_id"]
            )
        # prevent default subscription, handle it manually below
        res = super(
            MailActivity, self.with_context(mail_activity_noautofollow=True)
        ).write(vals)
        # subscribe new user if they allow activity-based subscription
        if "user_id" in vals and new_user_activities:
            new_user = self.env["res.users"].browse(vals["user_id"])
            if new_user.partner_id.auto_subscribe_on_activity:
                for res_model, model_activities in new_user_activities.grouped(
                    "res_model"
                ).items():
                    res_ids = list(set(model_activities.mapped("res_id")))
                    self.env[res_model].browse(res_ids).with_context(
                        mail_activity_autofollow=True
                    ).message_subscribe(partner_ids=new_user.sudo().partner_id.ids)
        return res
