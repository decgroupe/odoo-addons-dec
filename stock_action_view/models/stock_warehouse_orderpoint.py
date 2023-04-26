# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.model
    def action_view_base(self):
        return self.env.ref("stock.action_orderpoint").sudo().read()[0]

    def action_view(self):
        action = self.action_view_base()
        if not self.ids:
            pass
        elif len(self.ids) > 1:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", self.ids)]
        else:
            form = self.env.ref("stock.view_warehouse_orderpoint_form")
            action["views"] = [(form.id, "form")]
            action["res_id"] = self.ids[0]
        return action
