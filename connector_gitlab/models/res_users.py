# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    user_gitlab_resource_id = fields.Many2one(
        related="partner_id.user_gitlab_resource_id",
        string="GitLab User",
        inherited=True,
        readonly=False,
    )

    def _create_or_update_gitlab_user(self, password=False):
        self.ensure_one()
        user_uid = 0
        in_portal = self.env.ref("base.group_portal") in self.groups_id
        # We need to be sure that the GitLab user exists before trying to
        # edit it. Because a user can be in the portal but never having
        # been logged in.
        if in_portal and self.partner_id._signup_done():
            GitLab = self.env["gitlab.service"]
            user_uid = GitLab.create_or_update_user(
                self.id, self.email, self.name, password=password
            )
            if user_uid:
                if self.user_gitlab_resource_id:
                    if self.user_gitlab_resource_id.uid != user_uid:
                        self.user_gitlab_resource_id.uid = user_uid
                else:
                    self.user_gitlab_resource_id = (
                        self.user_gitlab_resource_id.sudo().create(
                            {
                                "type": "user",
                                "uid": user_uid,
                            }
                        )
                    )
        return user_uid

    def write(self, vals):
        res = super().write(vals)
        if "password" in vals:
            self._create_or_update_gitlab_user(vals.get("password"))
        return res
