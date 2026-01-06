# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

from odoo import Command, fields, models

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
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        token = self.sudo().delegate_signup_token
        return f"{base_url}/signup/delegate/{token}"

    def give_portal_access(self, force=False):
        PortalWizard = self.env["portal.wizard"]
        # unset active_id/active_ids otherwise wizard.user_ids will be filled with
        # garbage (because not check for `active_model` in `_default_user_ids`)
        wizard_id = (
            PortalWizard.with_context(active_id=False, active_ids=False)
            .sudo()
            .create({"partner_ids": [Command.set(self.ids)]})
        )
        for wizard_user_id in wizard_id.user_ids:
            if not wizard_user_id.is_portal:
                wizard_user_id.action_grant_access()
        return None
