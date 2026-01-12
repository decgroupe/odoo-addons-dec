# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from datetime import datetime

from odoo import models
from odoo.tools import format_amount, format_datetime


def format_currency_amount(amount, currency_id):
    pre = currency_id.position == "before"
    symbol = "{symbol}".format(symbol=currency_id.symbol or "")
    return "{pre}{0}{post}".format(
        amount, pre=symbol if pre else "", post=symbol if not pre else ""
    )


class Base(models.AbstractModel):
    _inherit = "base"

    def _get_assigned_extra_field_value(self, model, field_name, currency_field=None):
        IrModelFields = self.env["ir.model.fields"]
        # IrModelFieldsUs = self.with_context(lang='en_US').env['ir.model.fields']
        field_name_translated = IrModelFields.get_field_string(model._name)[field_name]
        key = (field_name, field_name_translated)
        value = model[field_name]
        field = model._fields[field_name]
        if isinstance(value, models.Model):
            if value:
                value = value.display_name
            else:
                value = False
        elif isinstance(value, datetime):
            value = format_datetime(self.env, value, self.env.user.tz)
        elif isinstance(value, float):
            if field.type == "monetary" and field.currency_field:
                currency_field = field.currency_field or currency_field
                if currency_field:
                    currency_id = model[currency_field]
                    value = format_amount(model.env, value, currency_id)
        return key, value
