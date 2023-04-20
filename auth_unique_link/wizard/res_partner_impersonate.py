# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

from odoo import fields, models, api, _


class ResPartnerImpersonate(models.TransientModel):
    _name = "res.partner.impersonate"
    _description = "Impersonate Portal User"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        readonly=True,
    )
    email = fields.Char(
        string="Sign-In Login",
        related="user_id.email",
    )
    token = fields.Char(
        string="Sign-In Code",
        related="user_id.signin_link_token",
    )
    expiration = fields.Datetime(
        string="Expiration",
        related="user_id.signin_link_expiration",
    )

    @api.model
    def default_get(self, fields):
        rec = super().default_get(fields)
        active_id = self._context.get("active_id")
        active_model = self._context.get("active_model")
        if active_model == "res.partner" and active_id:
            partner_id = self.env["res.partner"].browse(active_id)[0]
            user_id = partner_id.user_ids and partner_id.user_ids[0] or False
            if user_id and user_id.has_group("base.group_portal"):
                if not user_id.signin_link_valid:
                    expiration = user_id._get_signin_link_expiration_datetime()
                    user_id.signin_link_prepare(
                        expiration=expiration,
                        basic=True,
                    )
                rec.update(
                    {
                        "user_id": user_id.id,
                        "token": user_id.signin_link_token,
                        "expiration": user_id.signin_link_expiration,
                    }
                )
        return rec

    def action_generate_new_signin_link(self):
        self.ensure_one()
        expiration = self.user_id._get_signin_link_expiration_datetime()
        self.user_id.signin_link_prepare(
            expiration=expiration,
            basic=True,
        )
        return self._reopen()

    def _reopen(self, id=False):
        view_id = self.env.ref("auth_unique_link.res_partner_impersonate_form_view")
        act_window = self.env.ref("auth_unique_link.act_window_res_partner_impersonate")
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
