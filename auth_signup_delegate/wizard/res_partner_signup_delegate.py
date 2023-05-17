# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from odoo import fields, models, api, _


class ResPartnerSignupDelegate(models.TransientModel):
    _name = "res.partner.signup.delegate"
    _description = "Delegate Sign-up to Portal User"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        readonly=True,
    )
    token = fields.Char(
        string="Delegate Sign-up Token",
        related="user_id.delegate_signup_token",
        readonly=True,
    )
    url = fields.Char(
        string="Delegated Sign-up URL",
        readonly=True,
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")
        if active_model == "res.partner" and active_id:
            partner_id = self.env["res.partner"].browse(active_id)[0]
            user_id = partner_id.user_ids and partner_id.user_ids[0] or False
            rec.update(
                {
                    "user_id": user_id.id,
                    "url": user_id.partner_id.get_delegate_signup_url(),
                }
            )
        return rec

    def action_init_signup_delegation(self):
        self.ensure_one()
        self.user_id.partner_id.sudo().delegate_signup_prepare()
        self.url = self.user_id.partner_id.get_delegate_signup_url()
        return self._reopen()

    def action_cancel_signup_delegation(self):
        self.ensure_one()
        self.user_id.partner_id.sudo().delegate_signup_cancel()
        return self._reopen()

    def _reopen(self, id=False):
        view_id = self.env.ref(
            "auth_signup_delegate.res_partner_signup_delegate_form_view"
        )
        act_window = self.env.ref(
            "auth_signup_delegate.act_window_res_partner_signup_delegate"
        )
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "view_type": "form",
            "res_id": id or self.id,
            "res_model": self._name,
            "view_id": view_id.id,
            "name": act_window.name,
            "target": "new",
            "context": {
                "default_model": self._name,
            },
        }
