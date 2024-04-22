# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models


class Lead(models.Model):
    _inherit = "crm.lead"

    def _get_assigned_extra_values(self, type):
        self.ensure_one()
        res = {}

        if self.create_date:
            key, value = self._get_assigned_extra_field_value(
                self,
                "create_date",
            )
            res[key] = value
        if self.partner_id:
            key, value = self._get_assigned_extra_field_value(
                self,
                "partner_id",
            )
            res[key] = value
        if self.partner_shipping_id:
            key, value = self._get_assigned_extra_field_value(
                self,
                "partner_shipping_id",
            )
            res[key] = value
        if self.email_from:
            key, value = self._get_assigned_extra_field_value(
                self,
                "email_from",
            )
            res[key] = value
        if self.expected_revenue:
            key, value = self._get_assigned_extra_field_value(
                self,
                "expected_revenue",
            )
            res[key] = value
            if self.probability:
                _key, value = self._get_assigned_extra_field_value(
                    self,
                    "probability",
                )
                res[key] = ("%s (%s%%)") % (res[key], value)
        if self.date_deadline:
            key, value = self._get_assigned_extra_field_value(
                self,
                "date_deadline",
            )
            res[key] = value
        return res
