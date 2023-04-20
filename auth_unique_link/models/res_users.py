# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2021

import logging
import random
from datetime import datetime, timedelta

import werkzeug.urls

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied, UserError

_logger = logging.getLogger(__name__)


# Use same implementation from odoo.addons.auth_signup.models.res_partner
def random_token(n=20):
    # The token has an entropy of: 6 bits/char * n chars
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(random.SystemRandom().choice(chars) for _ in range(n))


def random_digit_token(n=6):
    # The token has an entropy of: 6 bits/char * n chars
    chars = "0123456789"
    return "".join(random.SystemRandom().choice(chars) for _ in range(n))


# Use same implementation from odoo.addons.auth_signup.models.res_partner
def now(**kwargs):
    return datetime.now() + timedelta(**kwargs)


class ResUsers(models.Model):
    _inherit = "res.users"

    signin_link_token = fields.Char(
        copy=False,
        groups="auth_unique_link.group_impersonate",
    )
    signin_link_expiration = fields.Datetime(
        copy=False,
        groups="auth_unique_link.group_impersonate",
    )
    signin_link_valid = fields.Boolean(
        compute="_compute_signin_link_valid",
        string="Signin Link Token is Valid",
    )
    signin_link_url = fields.Char(
        compute="_compute_signin_link_url",
        string="Signin URL",
    )

    @api.depends("signin_link_token", "signin_link_expiration")
    def _compute_signin_link_valid(self):
        dt = now()
        for rec, rec_sudo in zip(self, self.sudo()):
            rec.signin_link_valid = bool(rec_sudo.signin_link_token) and (
                not rec_sudo.signin_link_expiration
                or dt <= rec_sudo.signin_link_expiration
            )

    def _compute_signin_link_url(self):
        route = "login_link"
        for rec in self:
            base_url = rec.partner_id.get_base_url()
            query = {
                "db": self.env.cr.dbname,
                "login": rec.login,
                "token": rec.sudo().signin_link_token,
            }
            rec.signin_link_url = werkzeug.urls.url_join(
                base_url, "/web/%s?%s" % (route, werkzeug.urls.url_encode(query))
            )

    def signin_link_cancel(self):
        return self.write({"signin_link_token": False, "signin_link_expiration": False})

    def signin_link_prepare(self, expiration=False, basic=False):
        """generate a new token for the partners with the given validity, if
        necessary.

        :param expiration: the expiration datetime of the token
            (string, optional)
        """
        for rec in self:
            if expiration or not rec.signin_link_valid:
                while True:
                    if basic:
                        token = random_digit_token(6)
                    else:
                        token = random_token(32)
                    # In case of random has generated an already existing
                    # token check for it and and regenerate a new one
                    if not self._signin_link_retrieve_user(token):
                        break
                # We need to sudo since only admin user is allowed to write
                # other user fields
                rec.sudo().write(
                    {"signin_link_token": token, "signin_link_expiration": expiration}
                )
        return True

    @api.model
    def _signin_link_retrieve_user(
        self, token, uid=False, check_validity=False, raise_exception=False
    ):
        """Find the user corresponding to a token, and possibly check its
        validity.

        :param token: the token to resolve
        :param check_validity: if True, also check validity
        :param raise_exception: if True, raise exception instead of
            returning False
        :return: user (browse record) or False (if raise_exception is
            False)
        """
        domain = [("signin_link_token", "=", token)]
        if uid:
            domain.append(["id", "=", uid])
        user = self.search(domain, limit=1)
        if not user:
            if raise_exception:
                raise UserError(_("Signin link token '%s' is not valid") % token)
            return False
        if check_validity and not user.signin_link_valid:
            if raise_exception:
                raise UserError(_("Signin link token '%s' is no longer valid") % token)
            return False
        return user

    @api.model
    def _get_signin_link_expiration_minutes(self):
        ICP = self.env["ir.config_parameter"].sudo()
        expiration_minutes = int(ICP.get_param("auth_unique_link.expiration_minutes"))
        return expiration_minutes

    @api.model
    def _get_signin_link_expiration_datetime(self):
        expiration = self._get_signin_link_expiration_minutes() or False
        if expiration:
            expiration = now(minutes=+expiration)
        return expiration

    def _send_signin_link_email(self, basic=False):
        """Send notification email to a new portal user"""
        if not self.env.user.email:
            raise UserError(
                _(
                    "You must have an email address in your User Preferences to send emails."
                )
            )

        # Determine subject and body in the portal user's language
        if basic:
            template = self.env.ref("auth_unique_link.mail_template_signin_link_basic")
        else:
            template = self.env.ref("auth_unique_link.mail_template_signin_link")

        for rec in self:
            lang = rec.lang
            rec.signin_link_prepare(
                expiration=self._get_signin_link_expiration_datetime(),
                basic=basic,
            )

            if template:
                template = template.with_context(dbname=self._cr.dbname, lang=lang)
                template.send_mail(rec.id, force_send=True)
            else:
                _logger.warning(
                    "No email template found for sending " "sign-in link email"
                )

        return True

    def _check_credentials(self, password, env):
        try:
            return super(ResUsers, self)._check_credentials(password, env)
        except AccessDenied:
            res = self._signin_link_retrieve_user(
                token=password, uid=self.env.uid, check_validity=True
            )
            if not res:
                raise
