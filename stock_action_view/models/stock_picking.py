# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def action_view_base(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.stock_picking_action_picking_type"
        )
        return action

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("stock.view_picking_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.ids[0]
        return action
