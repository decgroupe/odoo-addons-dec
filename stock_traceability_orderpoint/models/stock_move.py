# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models

from odoo.addons.tools_miscellaneous.tools.html_helper import format_hd


class StockMove(models.Model):
    _inherit = "stock.move"

    orderpoint_created_production_ids = fields.Many2many(
        comodel_name="mrp.production",
        compute="_compute_orderpoint_created_orders",
        string="Created Production Orders by Orderpoint",
    )
    orderpoint_created_purchase_line_ids = fields.Many2many(
        comodel_name="purchase.order.line",
        compute="_compute_orderpoint_created_orders",
        string="Created Purchase Order Lines by Orderpoint",
    )

    @api.depends("product_id", "state", "procure_method")
    def _compute_orderpoint_created_orders(self):
        Orderpoint = self.env["stock.warehouse.orderpoint"]
        Production = self.env["mrp.production"]
        PurchaseLine = self.env["purchase.order.line"]
        self.orderpoint_created_production_ids = False
        self.orderpoint_created_purchase_line_ids = False
        for move in self:
            if move.procure_method == "make_to_stock" and move.state == "confirmed":
                reordering_rules = Orderpoint.search(
                    [("product_id", "=", move.product_id.id)]
                )
                if reordering_rules:
                    # Search for production orders created by mts rules
                    move.orderpoint_created_production_ids = Production.search(
                        [("orderpoint_id", "in", reordering_rules.ids)]
                    )
                    # Search for purchase orders created by mts rules
                    move.orderpoint_created_purchase_line_ids = PurchaseLine.search(
                        [("orderpoint_ids", "in", reordering_rules.ids)]
                    )

    def _get_mts_status(self, html=False):
        res = super()._get_mts_status(html)

        production_ids = self.orderpoint_created_production_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        for p in production_ids:
            head, desc = p.get_head_desc()
            res.append(format_hd("♻️⮡ " + head, desc, html))

        purchase_line_ids = self.orderpoint_created_purchase_line_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        for p in purchase_line_ids:
            head, desc = p.get_head_desc()
            res.append(format_hd("♻️⮡ " + head, desc, html))

        return res

    def _get_mto_created_items(self):
        res = super()._get_mto_created_items()
        if self.orderpoint_created_purchase_line_ids:
            action = self.orderpoint_created_purchase_line_ids.action_view()
            res["stock_traceability_orderpoint"] = {
                "priority": 20,
                "record": self.orderpoint_created_purchase_line_ids,
                "action": action,
            }
        elif self.orderpoint_created_production_ids:
            action = self.orderpoint_created_production_ids.action_view()
            res["stock_traceability_orderpoint"] = {
                "priority": 20,
                "record": self.orderpoint_created_production_ids,
                "action": action,
            }
        return res
