# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import api, models
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        """Overload create multiple to lowercase email."""
        for val in vals_list:
            val["email"] = val.get("email", "").lower()
        return super().create(vals_list)

    def write(self, vals):
        """Overload write to lowercase email."""
        if vals.get("email"):
            vals["email"] = vals["email"].lower()
        return super().write(vals)

    @api.model
    def _get_login_domain(self, login):
        domains = [
            super()._get_login_domain(login),
            [("email", "=", login.lower())],
        ]
        res = expression.OR(domains)
        return res
