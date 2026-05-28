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
    signin_link_token_failures = fields.Integer(
        copy=False,
        groups="auth_unique_link.group_impersonate",
    )

    @api.depends("signin_link_token", "signin_link_expiration")
    def _compute_signin_link_valid(self):
        dt = now()
        for rec, rec_sudo in zip(self, self.sudo(), strict=False):
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
                base_url,
                "/web/%s?%s" % (route, werkzeug.urls.url_encode(query)),  # noqa: UP031
            )

    def signin_link_cancel(self):
        """Cancel the current signin link token and reset the failure counter."""
        return self.write(
            {
                "signin_link_token": False,
                "signin_link_expiration": False,
                "signin_link_token_failures": 0,
            }
        )

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
                    {
                        "signin_link_token": token,
                        "signin_link_expiration": expiration,
                        "signin_link_token_failures": 0,
                    }
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
        user = self.sudo().search(domain, limit=1)
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
    def _signin_link_is_basic_token(self, token):
        """Return True if the token is a 6-digit numeric code (basic mode)."""
        return bool(token) and token.isdigit() and len(token) == 6

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
                    "You must have an email address in your "
                    "User Preferences to send emails."
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

    def _check_credentials(self, credential, env):
        """Override to support signin link token as a credential and track
        failed attempts for 6-digit tokens to prevent brute-force attacks.
        """
        try:
            return super()._check_credentials(credential, env)
        except AccessDenied:
            if not (credential["type"] == "password" and credential.get("password")):
                raise
            password = credential.get("password")
            res = self._signin_link_retrieve_user(
                token=password, uid=self.env.uid, check_validity=True
            )
            if not res:
                # increment failure counter when a 6-digit code is submitted
                # to limit brute-force; clear the token after 3 failures so
                # the user must request a new one.
                # use a dedicated cursor for both the read and the write so
                # that (a) we see the latest committed token value (bypassing
                # any stale ORM cache on the auth cursor) and (b) the write
                # survives the auth cursor rollback that follows AccessDenied.
                if self._signin_link_is_basic_token(password):
                    with self.env.registry.cursor() as cr:
                        user = self.env(cr=cr)["res.users"].sudo().browse(self.env.uid)
                        if user.exists() and self._signin_link_is_basic_token(
                            user.signin_link_token
                        ):
                            failures = user.signin_link_token_failures + 1
                            if failures >= 3:
                                _logger.warning(
                                    "signin link token for user %s cleared after "
                                    "%d failed attempts",
                                    user.login,
                                    failures,
                                )
                                user.signin_link_cancel()
                            else:
                                user.write({"signin_link_token_failures": failures})
                            user.env.flush_all()
                raise
