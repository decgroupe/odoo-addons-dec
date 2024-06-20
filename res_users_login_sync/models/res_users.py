# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2022

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        # base class will set the active status to its own partner, to avoid a bouncing
        # effect, archive change propagation is disabled here
        users = super(ResUsers, self.with_context(user_archive_change=True)).create(
            vals_list
        )
        return users

    def toggle_active(self):
        super(
            ResUsers, self.with_context(toggle_active_from_users=True)
        ).toggle_active()

    def _notify_login_sync(self, previous_login, new_login):
        self.ensure_one()
        template_id = self.env.ref("res_users_login_sync.email_template_login_edit")
        ctx = {
            "previous_login": previous_login,
            "new_login": new_login,
        }
        template_id.with_context(**ctx).send_mail(
            self.id,
            force_send=True,
            email_values=self._get_notify_login_sync_email_values(
                previous_login,
                new_login,
            ),
        )

    def _get_notify_login_sync_email_values(self, previous_login, new_login):
        return {
            "email_to": new_login,
            "email_cc": previous_login,
        }
