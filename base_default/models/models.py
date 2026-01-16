# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import inspect

from odoo import api, models


class BaseModel(models.AbstractModel):
    _inherit = "base"

    @api.model
    def default_get(self, fields_list):
        edit_values = {}
        # use frame introspection to retrieve the "values" argument of the caller
        # (onchange, ...)
        frame = inspect.currentframe()
        while frame.f_back:
            frame = frame.f_back
            values = frame.f_locals.get("values", None)
            if values and isinstance(values, dict):
                edit_values = values
                break

        return super(
            BaseModel,
            self.with_context(edit_values=edit_values),
        ).default_get(fields_list)
