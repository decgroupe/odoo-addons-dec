# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_gitlab_resource_id = fields.Many2one(
        related='partner_id.user_gitlab_resource_id',
        string='GitLab User',
        inherited=True,
        readonly=False,
    )

    def _create_or_update_gitlab_user(self, password):
        self.ensure_one()
        in_portal = self.env.ref('base.group_portal') in self.groups_id
        if in_portal:
            GitLab = self.env['gitlab.service']
            id = GitLab.create_or_update_user(
                self.id, self.email, self.name, password=password
            )
            if id:
                if self.user_gitlab_resource_id:
                    if self.user_gitlab_resource_id.backend_id != id:
                        self.user_gitlab_resource_id.backend_id = id
                else:
                    self.user_gitlab_resource_id = self.user_gitlab_resource_id.create(
                        {
                            'type': 'user',
                            'backend_id': id,
                        }
                    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'password' in vals:
            self._create_or_update_gitlab_user(vals.get('password'))
        return res
