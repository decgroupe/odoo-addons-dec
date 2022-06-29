# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

import logging
import re
import ipaddress

from odoo import _, api, fields, models
from odoo.exceptions import UserError, AccessDenied
from odoo.http import request

_logger = logging.getLogger(__name__)

from odoo.addons import base


def is_ip_private(ip):
    # https://en.wikipedia.org/wiki/Private_network

    priv_lo = re.compile(r"^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    priv_24 = re.compile(r"^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    priv_20 = re.compile(r"^192\.168\.\d{1,3}.\d{1,3}$")
    priv_16 = re.compile(r"^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$")

    res = priv_lo.match(ip) or priv_24.match(ip) or priv_20.match(
        ip
    ) or priv_16.match(ip)
    return res is not None


class ResUsers(models.Model):
    _inherit = 'res.users'

    local_password = fields.Char(
        inverse='_set_local_password',
        copy=False,
        help="This password can only be used from a private IP address",
    )

    def __init__(self, pool, cr):
        """ Override of __init__ to add access rights on new fields.
            Access rights are disabled by default, but allowed on some 
            specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        init_res = super().__init__(pool, cr)
        type(self).SELF_WRITEABLE_FIELDS = list(
            set(self.SELF_WRITEABLE_FIELDS + ['local_password'])
        )
        return init_res

    def _get_ip_address(self):
        ip_addr = request.httprequest.environ.get('HTTP_X_FORWARDED_FOR')
        if ip_addr:
            ip_addr = ip_addr.split(',')[0]
        else:
            ip_addr = request.httprequest.remote_addr
        return ip_addr

    def _set_encrypted_local_password(self, uid, pw):
        assert self._crypt_context().identify(pw) != 'plaintext'
        self.env.cr.execute(
            'UPDATE res_users SET local_password=%s WHERE id=%s', (pw, uid)
        )
        self.invalidate_cache(['local_password'], [uid])

    def _clear_local_password(self, uid):
        self.env.cr.execute(
            'UPDATE res_users SET local_password=NULL WHERE id=%s', (uid, )
        )
        self.invalidate_cache(['local_password'], [uid])

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

    def _check_credentials(self, password):
        try:
            is_local = ipaddress.ip_address(self._get_ip_address()).is_private
            return super(ResUsers, self.with_context(bypass_mfa=is_local)).\
                _check_credentials(password)
        except AccessDenied as e:
            valid = False
            if self.user_has_groups('auth_local_password.group_local_password'):
                self.env.cr.execute(
                    "SELECT COALESCE(local_password, '') "
                    "FROM res_users WHERE id=%s", [self.env.user.id]
                )
                [hashed] = self.env.cr.fetchone()
                valid, replacement = self._crypt_context().verify_and_update(
                    password, hashed
                )
                if replacement is not None:
                    self._set_encrypted_local_password(
                        self.env.user.id, replacement
                    )
                if valid and not is_local:
                    raise AccessDenied(
                        _("Cannot use a local password from Internet")
                    ) from e
            if not valid:
                raise
