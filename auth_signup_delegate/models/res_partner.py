# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models, api
from odoo.addons.auth_signup.models.res_partner import random_token


class ResPartner(models.Model):
    _inherit = "res.partner"

    delegate_signup_token = fields.Char(
        copy=False,
        groups="base.group_erp_manager",
    )

    @api.multi
    def delegate_signup_cancel(self):
        return self.write({
            'delegate_signup_token': False,
        })

    @api.multi
    def delegate_signup_prepare(self):
        """ Generate a new token for the partners if necessary
        """
        for partner in self:
            if not partner.delegate_signup_token:
                partner.write({
                    'delegate_signup_token': random_token(),
                })
        return True

    @api.multi
    def get_delegate_signup_url(self):
        self.ensure_one()
        return "%s/signup/delegate/%s" % (
            self.env['ir.config_parameter'].get_param('web.base.url'),
            self.delegate_signup_token
        )
