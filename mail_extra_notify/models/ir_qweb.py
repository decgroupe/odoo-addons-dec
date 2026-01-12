# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    def _get_assigned_record(self, values):
        res = False
        record = False
        if "activity" in values or self.env.context.get("activity"):
            res = "activity"
            if "activity" in values:
                # Note that there is not always an activity in values with Odoo 18.0
                model = values["activity"].res_model
                res_id = values["activity"].res_id
                record = self.env[model].browse(res_id)
            elif self.env.context.get("activity"):
                # activity from context is added from a custom commit:
                # [DEC][IMP] mail: Add activity in context before notify
                record = self.env.context.get("activity")
        elif "object" in values:
            record = values.get("object")
            if record._name == "res.partner":
                res = "user"
        elif "record" in values:
            record = values.get("record")
        return res, record

    @api.model
    def _render(self, id_or_xml_id, values=None, **options):
        assigned_type, record = self._get_assigned_record(values)
        if record:
            # Add extra information in notify message
            if hasattr(record, "_get_assigned_extra_values"):
                extra_values = record._get_assigned_extra_values(assigned_type)
                values["extra_values"] = extra_values
        res = super()._render(id_or_xml_id, values=values, **options)
        return res
