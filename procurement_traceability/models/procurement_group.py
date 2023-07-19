# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    # addons/stock/models/stock_picking.py
    picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="group_id",
    )
    picking_count = fields.Integer(
        compute="_compute_picking",
        string="Picking count",
        default=0,
        store=False,
    )
    # addons/stock/models/stock_warehouse.py
    orderpoint_ids = fields.One2many(
        comodel_name="stock.warehouse.orderpoint",
        inverse_name="group_id",
    )
    orderpoint_count = fields.Integer(
        compute="_compute_orderpoint",
        string="Reordering rules count",
        default=0,
        store=False,
    )
    # addons/stock/models/stock_rule.py
    stock_rule_ids = fields.One2many(
        comodel_name="stock.rule",
        inverse_name="group_id",
    )
    stock_rule_count = fields.Integer(
        compute="_compute_stock_rule",
        string="Route count",
        default=0,
        store=False,
    )
    # addons/stock/models/stock_move.py
    stock_move_ids = fields.One2many(
        comodel_name="stock.move",
        inverse_name="group_id",
    )
    stock_move_count = fields.Integer(
        compute="_compute_stock_move",
        string="Stock move count",
        default=0,
        store=False,
    )
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
    # addons/mrp/models/mrp_production.py
    mrp_production_ids = fields.One2many(
        comodel_name="mrp.production",
        inverse_name="procurement_group_id",
    )
    mrp_production_count = fields.Integer(
        compute="_compute_mrp_production_order",
        string="Production count",
        default=0,
        store=False,
    )
    # odoo-addons/oca/purchase-workflow/purchase_line_procurement_group/models/purchase.py
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

    def _compute_picking(self):
        for procurement in self:
            procurement.picking_count = len(procurement.picking_ids)

    def _compute_orderpoint(self):
        for procurement in self:
            procurement.orderpoint_count = len(procurement.orderpoint_ids)

    def _compute_stock_rule(self):
        for procurement in self:
            procurement.stock_rule_count = len(procurement.stock_rule_ids)

    def _compute_stock_move(self):
        for procurement in self:
            procurement.stock_move_count = len(procurement.stock_move_ids)

    def _compute_sale_order(self):
        for procurement in self:
            procurement.sale_order_count = len(procurement.sale_order_ids)

    def _compute_purchase_order(self):
        for procurement in self:
            procurement.purchase_order_count = len(procurement.purchase_order_ids)

    def _compute_mrp_production_order(self):
        for procurement in self:
            procurement.mrp_production_count = len(procurement.mrp_production_ids)

    def _compute_purchase_order_line(self):
        for procurement in self:
            procurement.purchase_order_line_count = len(
                procurement.purchase_order_line_ids
            )

    def action_view_pickings(self):
        self.ensure_one()
        action = self.env["stock.picking"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_orderpoints(self):
        self.ensure_one()
        action = self.env["stock.warehouse.orderpoint"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_stock_rules(self):
        self.ensure_one()
        action = self.env["stock.rule"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_stock_moves(self):
        self.ensure_one()
        action = self.env["stock.move"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {"group_by": "origin"}
        return action

    def action_view_sale_orders(self):
        self.ensure_one()
        action = self.env["sale.order"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_purchase_orders(self):
        self.ensure_one()
        action = self.env["purchase.order"].action_view()
        action["domain"] = [("group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_mrp_productions(self):
        self.ensure_one()
        action = self.env["mrp.production"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_purchase_order_lines(self):
        self.ensure_one()
        action = self.env["purchase.order.line"].action_view()
        action["domain"] = [("procurement_group_id", "=", self.id)]
        action["context"] = {}
        return action
