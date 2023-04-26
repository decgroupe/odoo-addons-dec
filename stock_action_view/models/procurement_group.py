# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import _, api, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    @api.model
    def action_view_base(self):
        return {
            "name": _("Procurement Group(s)"),
            "type": "ir.actions.act_window",
            "res_model": "procurement.group",
            "target": "current",
            "view_mode": "tree,form",
        }

    def action_view(self):
        action = self.action_view_base()
        form = self.env.ref("stock.procurement_group_form_view")
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            # tree = self.env.ref("???")
            action["domain"] = [("id", "in", self.ids)]
            action["views"] = [(False, "tree"), (form.id, "form")]
            action["view_mode"] = "tree,form"
        else:
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.ids[0]
        return action
