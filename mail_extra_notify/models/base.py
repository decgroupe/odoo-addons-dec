# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2022

from datetime import datetime

from odoo import models
from odoo.tools import format_datetime


def format_currency_amount(amount, currency_id):
    pre = currency_id.position == "before"
    symbol = "{symbol}".format(symbol=currency_id.symbol or "")
    return "{pre}{0}{post}".format(
        amount, pre=symbol if pre else "", post=symbol if not pre else ""
    )


class Base(models.AbstractModel):
    _inherit = "base"

    def _get_assigned_extra_field_value(self, model, field_name):
        IrTranslation = self.env["ir.translation"]
        field_name_translated = IrTranslation.get_field_string(model._name)[field_name]
        key = (field_name, field_name_translated)
        value = model[field_name]
        field = model._fields[field_name]
        if isinstance(value, models.Model):
            if value:
                value = value.name_get()[0][1]
            else:
                value = False
        elif isinstance(value, datetime):
            value = format_datetime(self.env, value, self.env.user.tz)
        elif isinstance(value, float):
            if field.type == "monetary":
                currency_id = model[field.currency_field]
                value = format_currency_amount(value, currency_id)
        return key, value
