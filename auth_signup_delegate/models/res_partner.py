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

    def delegate_create_contact(self, vals):
        return self.create(vals)

    @api.multi
    def get_delegate_signup_url(self):
        self.ensure_one()
        return "%s/signup/delegate/%s" % (
            self.env['ir.config_parameter'].get_param('web.base.url'),
            self.sudo().delegate_signup_token
        )

    @api.multi
    def give_portal_access(self):
        PortalWizard = self.env['portal.wizard']
        PortalWizardUser = self.env['portal.wizard.user']
        wizard_id = PortalWizard.sudo().create({})
        for partner_id in self:
            already_in_portal = False
            if partner_id.user_ids:
                already_in_portal = self.env.ref(
                    'base.group_portal'
                ) in partner_id.user_ids[0].groups_id
            if not already_in_portal:
                vals = {
                    'wizard_id': wizard_id.id,
                    'partner_id': partner_id.id,
                    'email': partner_id.email,
                    'in_portal': True,
                }
                wizard_user_id = PortalWizardUser.sudo().create(vals)
        return wizard_id.action_apply()
