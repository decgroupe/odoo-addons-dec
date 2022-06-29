# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def write(self, vals):
        previous_emails = {}
        if 'email' in vals:
            for rec in self:
                previous_emails[rec.id] = rec.email
        res = super().write(vals)
        if 'email' in vals:
            for rec in self.filtered('user_ids'):
                previous_email = previous_emails.get(rec.id, False)
                for user_id in rec.user_ids:
                    if user_id.login == previous_email:
                        user_id.login = user_id.partner_id.email
        return res
