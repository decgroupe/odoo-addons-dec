# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    # addons/purchase_stock/models/purchase.py
    purchase_order_ids = fields.One2many(
        comodel_name="purchase.order",
        inverse_name="group_id",
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order",
        string="Purchase count",
        default=0,
        store=False,
    )
    # ./oca/purchase-workflow/purchase_line_procurement_group/models/purchase.py
    purchase_order_line_ids = fields.One2many(
        comodel_name="purchase.order.line",
        inverse_name="procurement_group_id",
    )
    purchase_order_line_count = fields.Integer(
        compute="_compute_purchase_order_line",
        string="Purchase lines count",
        default=0,
        store=False,
    )

    def _compute_purchase_order(self):
        for procurement in self:
            procurement.purchase_order_count = len(procurement.purchase_order_ids)

    def _compute_purchase_order_line(self):
        for procurement in self:
            procurement.purchase_order_line_count = len(
                procurement.purchase_order_line_ids
            )

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env["purchase.order"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_purchase_order_lines(self):
        self.ensure_one()
        action = self.env["purchase.order.line"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action
