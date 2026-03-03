# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

from odoo import models

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = "base"

    def _apply_onchange_method(self, field_name, method):
        self_context = self.with_context(onchange_sender=field_name)
        return super(Base, self_context)._apply_onchange_method(field_name, method)

    def onchange(self, values: dict, field_names: list[str], fields_spec: dict):
        self_context = self.with_context(onchange_values=values)
        return super(Base, self_context).onchange(values, field_names, fields_spec)
