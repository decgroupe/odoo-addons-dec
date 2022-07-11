# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _get_user_assigned_extra_values(self):
        self.ensure_one()
        res = {}

        if self.origin:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'origin',
            )
            res[key] = value
        if self.partner_shipping_id:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'partner_shipping_id',
            )
            res[key] = value
        # State
        key, value = self._get_user_assigned_extra_field_value(
            self,
            'state',
        )
        # Total
        key, value = self._get_user_assigned_extra_field_value(
            self,
            'amount_total',
        )
        res[key] = value
        return res

    def _get_user_assigned_extra_field_value(self, model, field_name):
        IrTranslation = self.env['ir.translation']
        key = IrTranslation.get_field_string(model._name)[field_name]
        value = model[field_name]
        if isinstance(value, models.Model):
            value = value.name_get()[0][1]
        return key, value
