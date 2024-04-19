# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from datetime import datetime

from odoo import models
from odoo.tools import format_datetime

class Base(models.AbstractModel):
    _inherit = "base"

    def _get_assigned_extra_field_value(self, model, field_name):
        IrTranslation = self.env["ir.translation"]
        key = IrTranslation.get_field_string(model._name)[field_name]
        value = model[field_name]
        if isinstance(value, models.Model):
            if value:
                value = value.name_get()[0][1]
            else:
                value = False
        elif isinstance(value, datetime):
            value = format_datetime(self.env, value, self.env.user.tz)
        return key, value
