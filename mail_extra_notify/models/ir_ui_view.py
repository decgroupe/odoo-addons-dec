# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _get_assigned_type(self):
        if self.id == self.env.ref("mail.message_user_assigned").id:
            res = "user"
        elif self.id == self.env.ref("mail.message_activity_assigned").id:
            res = "activity"
        else:
            res = False
        return res

    def _render(self, values=None, engine="ir.qweb", minimal_qcontext=False):
        assigned_type = self._get_assigned_type()
        if values and assigned_type:
            if assigned_type == "user":
                record = values.get("object")
            elif assigned_type == "activity":
                model = values["activity"].res_model
                id = values["activity"].res_id
                record = self.env[model].browse(id)
            # Add extra information in notify message
            if record and hasattr(record, "_get_assigned_extra_values"):
                extra_values = record._get_assigned_extra_values(assigned_type)
                values["extra_values"] = extra_values
        res = super()._render(
            values=values, engine=engine, minimal_qcontext=minimal_qcontext
        )
        return res
