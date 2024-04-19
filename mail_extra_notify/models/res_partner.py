# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_user_assigned_extra_values(self):
        self.ensure_one()
        res = {}

        if self.email:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                "email",
            )
            res[key] = value
        if self.create_uid:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                "create_uid",
            )
            res[key] = value
        if self.create_date:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                "create_date",
            )
            res[key] = value
        return res
