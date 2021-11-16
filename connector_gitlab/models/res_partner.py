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
        if 'email' in vals:
            previous_emails = {}
            for rec in self:
                previous_emails[rec.id] = rec.email
        res = super().write(vals)
        if 'email' in vals or 'name' in vals:
            for rec in self.filtered('user_ids'):
                user_id = rec.user_ids
                user_id.ensure_one()
                previous_email = previous_emails.get(rec.id, False)
                if previous_email:
                    user_id = user_id.with_context(
                        search_email=previous_email
                    )
                user_id._create_or_update_gitlab_user()
        return res
