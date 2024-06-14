# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import api, fields, models, api
from odoo.addons.auth_signup.models.res_partner import random_token


class ResPartner(models.Model):
    _inherit = "res.partner"

    delegate_signup_token = fields.Char(
        string="Delegate Sign-up Token",
        groups="base.group_erp_manager",
        copy=False,
    )

    def delegate_signup_cancel(self):
        return self.write({"delegate_signup_token": False})

    def delegate_signup_prepare(self):
        """Generate a new token for the partners if necessary"""
        for partner in self:
            if not partner.delegate_signup_token:
                partner.write({"delegate_signup_token": random_token()})
        return True

    def delegate_create_contact(self, vals):
        return self.create(vals)

    def get_delegate_signup_url(self):
        self.ensure_one()
        return "%s/signup/delegate/%s" % (
            self.env["ir.config_parameter"].sudo().get_param("web.base.url"),
            self.sudo().delegate_signup_token,
        )

    def give_portal_access(self, force=False):
        PortalWizard = self.env["portal.wizard"]
        PortalWizardUser = self.env["portal.wizard.user"]
        # unset active_id/active_ids otherwise wizard.user_ids will be filled with
        # garbage (because not check for `active_model` in `_default_user_ids`)
        wizard_id = (
            PortalWizard.with_context(active_id=False, active_ids=False)
            .sudo()
            .create({})
        )
        for partner_id in self:
            already_in_portal = False
            if partner_id.user_ids:
                already_in_portal = (
                    self.env.ref("base.group_portal")
                    in partner_id.user_ids[0].groups_id
                )
            if force or not already_in_portal:
                vals = {
                    "wizard_id": wizard_id.id,
                    "partner_id": partner_id.id,
                    "email": partner_id.email,
                    "in_portal": True,
                }
                wizard_user_id = PortalWizardUser.sudo().create(vals)
        return wizard_id.action_apply()
