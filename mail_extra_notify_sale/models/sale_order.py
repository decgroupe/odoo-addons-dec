# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_user_assigned_extra_values(self):
        self.ensure_one()
        res = {}

        if self.opportunity_id:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'opportunity_id',
            )
            res[key] = value
        if self.partner_shipping_id:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'partner_shipping_id',
            )
            res[key] = value
        if self.partner_shipping_zip_id:
            key, value = self._get_user_assigned_extra_field_value(
                self,
                'partner_shipping_zip_id',
            )
            res[key] = value
        # Total
        key, value = self._get_user_assigned_extra_field_value(
            self,
            'amount_total',
        )
        res[key] = value
        return res
