# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

import ipaddress
import logging
import re

from odoo import _, api, fields, models
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request

_logger = logging.getLogger(__name__)

from odoo.addons import base


class ResUsers(models.Model):
    _inherit = "res.users"

    local_password = fields.Char(
        inverse="_set_local_password",
        copy=False,
        help="This password can only be used from a private IP address",
    )

    def __init__(self, pool, cr):
        """Override of __init__ to add access rights on new fields.
        Access rights are disabled by default, but allowed on some
        specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(self.SELF_WRITEABLE_FIELDS + ["local_password"])
        )
        return init_res

    def _get_ip_address(self):
        ip_addr = (
            request.httprequest.environ.get("HTTP_X_FORWARDED_FOR")
            if request
            else False
        )
        if ip_addr:
            ip_addr = ip_addr.split(",")[0]
        else:
            ip_addr = request.httprequest.remote_addr if request else False
        return ip_addr

    def _set_encrypted_local_password(self, uid, pw):
        assert self._crypt_context().identify(pw) != "plaintext"
        self.env.cr.execute(
            "UPDATE res_users SET local_password=%s WHERE id=%s", (pw, uid)
        )
        self.invalidate_cache(["local_password"], [uid])

    def _clear_local_password(self, uid):
        self.env.cr.execute(
            "UPDATE res_users SET local_password=NULL WHERE id=%s", (uid,)
        )
        self.invalidate_cache(["local_password"], [uid])

    def _check_local_password(self, pw):
        if pw and len(pw) < 4:
            raise UserError(
                _(
                    "Your local password does not meet the minimum "
                    "length (4 characters)"
                )
            )

    def _set_local_password(self):
        ctx = self._crypt_context()
        for user in self:
            pw = user.local_password and user.local_password.strip()
            if pw is False:
                self._clear_local_password(user.id)
            else:
                self._check_local_password(pw)
                self._set_encrypted_local_password(user.id, ctx.encrypt(pw))

    def _check_credentials(self, password, env):
        try:
            is_local = ipaddress.ip_address(self._get_ip_address()).is_private
            return super(
                ResUsers, self.with_context(bypass_mfa=is_local)
            )._check_credentials(password, env)
        except AccessDenied as e:
            valid = False
            # Verifies the local password, possibly updating the stored hash if needed
            if self.user_has_groups("auth_local_password.group_local_password"):
                self.env.cr.execute(
                    "SELECT COALESCE(local_password, '') " "FROM res_users WHERE id=%s",
                    [self.env.user.id],
                )
                [hashed] = self.env.cr.fetchone()
                valid, replacement = self._crypt_context().verify_and_update(
                    password, hashed
                )
                if replacement is not None:
                    self._set_encrypted_local_password(self.env.user.id, replacement)
                if valid and not is_local:
                    raise AccessDenied(
                        _("Cannot use a local password from Internet")
                    ) from e
            if not valid:
                raise
