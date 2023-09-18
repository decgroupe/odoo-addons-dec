# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def action_view_base(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_orders"
        )
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("sale.view_order_form", False)
            form_view = [(form and form.id or False, "form")]
            if "views" in action:
                action["views"] = form_view + [
                    (state, view) for state, view in action["views"] if view != "form"
                ]
            else:
                action["views"] = form_view
            action["res_id"] = self.ids[0]
        return action
