# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from odoo import models, api, fields


class Base(models.AbstractModel):
    _inherit = 'base'

    def _get_user_assigned_extra_field_value(self, model, field_name):
        IrTranslation = self.env['ir.translation']
        key = IrTranslation.get_field_string(model._name)[field_name]
        value = model[field_name]
        if isinstance(value, models.Model):
            if value:
                value = value.name_get()[0][1]
            else:
                value = False
        return key, value
