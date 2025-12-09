# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import _, api, models
from odoo.exceptions import AccessError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        active = vals.get("active")
        if not self.env.context.get("user_archive_change") and not self.env.context.get(
            "toggle_active_from_users"
        ):
            # we use sudo to change archive status, that's why we need to check that
            # the user have minimum rights on contact editing
            archive_change_allowed = self.user_has_groups("base.group_partner_manager")
            self_ca = self.with_context(user_archive_change=True)
            if archive_change_allowed:
                self_ca = self_ca.sudo()
            if active is False:
                self_ca._archive_users()
            elif active is True:
                self_ca._unarchive_users()
        previous_emails = self._previous_emails_mapping(vals)
        res = super().write(vals)
        if previous_emails:
            self._sync_login(previous_emails)
        return res

    def _check_archive_change(self, user_ids):
        if (
            not self.env.user._is_admin()
            and self.env.ref("base.group_user") in user_ids.groups_id
        ):
            raise AccessError(
                _(
                    "Only administrators are allowed to archive/unarchive "
                    "internal users from their partner!"
                )
            )

    def _post_archive_change(self, user_ids, action):
        self.message_post_with_view(
            views_or_xmlid="res_users_login_sync.user_archive_change",
            values={
                "action": action,
                "current_user": self.env.user,
                "users": user_ids,
            },
            subtype_id=self.env.ref("mail.mt_note").id,
        )

    def _archive_users(self):
        for partner in self:
            user_ids = partner.user_ids
            self._check_archive_change(user_ids)
            if partner.active and user_ids:
                partner._post_archive_change(user_ids, _("archived"))
                user_ids.action_archive()

    def _unarchive_users(self):
        for partner in self:
            user_ids = partner.with_context(active_test=False).user_ids
            self._check_archive_change(user_ids)
            if (
                not partner.active
                and user_ids
                and any(not user.active for user in user_ids)
            ):
                partner._post_archive_change(user_ids, _("unarchived"))
                user_ids.action_unarchive()

    @api.model
    def _previous_emails_mapping(self, vals):
        res = {}
        if "email" in vals:
            for rec in self:
                res[rec.id] = rec.email
        return res

    def _sync_login(self, previous_emails):
        sync_allowed = self.user_has_groups(
            "res_users_login_sync.group_user_login_sync"
        )
        for rec in self.filtered("user_ids"):
            previous_email = previous_emails.get(rec.id, False)
            for user_id in rec.user_ids:
                if user_id.login == previous_email:
                    if sync_allowed or user_id == self.env.user:
                        previous_login = user_id.sudo().login
                        user_id.sudo().login = user_id.partner_id.email
                        user_id._notify_login_sync(
                            previous_login, user_id.partner_id.email
                        )
                    else:
                        rec.message_post_with_view(
                            views_or_xmlid="res_users_login_sync.login_sync_warning_template",
                            values={
                                "contact_email": user_id.partner_id.email,
                                "user_login": user_id.sudo().login,
                            },
                            subtype_id=self.env.ref("mail.mt_note").id,
                        )
