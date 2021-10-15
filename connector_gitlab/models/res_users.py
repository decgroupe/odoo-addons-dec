# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    # gitlab_mapping_id = fields.Many2one(
    #     'gitlab.resource',
    #     string='GitLab ID',
    # )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if 'password' in vals:
            GitLab = self.env['gitlab.service']
            password = vals.get('password')
            if self.gitlab_mapping_id:
                GitLab.update_user(
                    self.id, password=password
                )
            else:
                GitLab.create_user(self.id, self.email, password)
        return res
