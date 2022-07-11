# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models, api, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    def _get_user_assigned_extra_values(self):
        self.ensure_one()
        res = {}

        if self.sale_line_id:
            key, value = self._get_user_assigned_extra_field_value(
                res,
                self,
                'sale_line_id',
            )
            res[key] = value
            key, value = self._get_user_assigned_extra_field_value(
                res,
                self.sale_line_id.order_id,
                'partner_shipping_id',
            )
            res[key] = value
            key, value = self._get_user_assigned_extra_field_value(
                res,
                self,
                'partner_shipping_zip_id',
            )
            res[key] = value
        return res

    def _get_user_assigned_extra_field_value(self, res, model, field_name):
        IrTranslation = self.env['ir.translation']
        key = IrTranslation.get_field_string(model._name)[field_name]
        value = model[field_name].name_get()[0][1]
        return key, value
