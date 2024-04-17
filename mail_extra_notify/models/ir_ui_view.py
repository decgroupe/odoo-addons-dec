# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models


class IrUiView(models.Model):
    _inherit = "ir.ui.view"

    def _render(self, values=None, engine="ir.qweb", minimal_qcontext=False):
        if self.id == self.env.ref("mail.message_user_assigned").id:
            # Add extra information in notify message
            model = values.get("object")
            if model and hasattr(model, "_get_user_assigned_extra_values"):
                extra_values = model._get_user_assigned_extra_values()
                values["extra_values"] = extra_values
        res = super()._render(
            values=values, engine=engine, minimal_qcontext=minimal_qcontext
        )
        return res
