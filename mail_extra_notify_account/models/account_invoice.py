# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_assigned_extra_values(self, type):
        self.ensure_one()
        res = {}

        if self.invoice_origin:
            key, value = self._get_assigned_extra_field_value(
                self,
                "invoice_origin",
            )
            res[key] = value
        if self.partner_shipping_id:
            key, value = self._get_assigned_extra_field_value(
                self,
                "partner_shipping_id",
            )
            res[key] = value
        # State
        key, value = self._get_assigned_extra_field_value(
            self,
            "state",
        )
        res[key] = value
        # Total
        key, value = self._get_assigned_extra_field_value(
            self,
            "amount_total",
        )
        res[key] = value
        return res
