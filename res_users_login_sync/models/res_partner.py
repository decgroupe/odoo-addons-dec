# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        previous_emails = self._previous_emails_mapping(vals)
        res = super().write(vals)
        if previous_emails:
            self._sync_login(previous_emails)
        return res

    @api.model
    def _previous_emails_mapping(self, vals):
        res = {}
        if 'email' in vals:
            for rec in self:
                res[rec.id] = rec.email
        return res

    @api.multi
    def _sync_login(self, previous_emails):
        sync_allowed = self.user_has_groups(
            'res_users_login_sync.group_user_login_sync'
        )
        for rec in self.filtered('user_ids'):
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
                            views_or_xmlid=
                            'res_users_login_sync.login_sync_warning_template',
                            values={
                                'contact_email': user_id.partner_id.email,
                                'user_login': user_id.sudo().login,
                            },
                            subtype_id=self.env.ref('mail.mt_note').id
                        )
