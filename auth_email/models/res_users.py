# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import _, api, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def _get_login_domain(self, login):
        res = super()._get_login_domain(login)
        login_domain = ("login", "=", login)
        email_domain = ("email", "=", login)
        if res[0] == login_domain:
            res.pop(0)
            res = [("|"), login_domain, email_domain] + res
        return res
