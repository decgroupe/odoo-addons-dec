# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    # addons/sale_stock/models/sale_order.py
    sale_order_ids = fields.One2many(
        comodel_name="sale.order",
        inverse_name="procurement_group_id",
        string="Sale Orders",
    )
    sale_order_count = fields.Integer(
        compute="_compute_sale_order",
        string="Sale count",
        default=0,
        store=False,
    )

    def _compute_sale_order(self):
        for procurement in self:
            procurement.sale_order_count = len(procurement.sale_order_ids)

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env["sale.order"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action
