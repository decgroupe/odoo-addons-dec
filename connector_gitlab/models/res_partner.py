# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    user_gitlab_resource_id = fields.Many2one(
        'gitlab.resource',
        string='GitLab User',
    )

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if len(self.user_ids) == 1:
            if 'email' in vals or 'name' in vals:
                self.user_ids._create_or_update_gitlab_user()
        return res
