# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    production_id = fields.Many2one(
        comodel_name="mrp.production",
        string="Production Order",
        compute="_compute_production_id",
    )
    production_ids = fields.Many2many(
        comodel_name="mrp.production",
        relation="purchase_order_line_mrp_rel",
        column1="purchase_line_id",
        column2="production_id",
        string="Production Orders",
        readonly=True,
        copy=False,
        help="Production order that created this line",
    )
    bom_line_id = fields.Many2one(
        comodel_name="mrp.bom.line",
        string="Line of the Bill of Material",
    )

    @api.depends("production_ids")
    def _compute_production_id(self):
        for p in self:
            p.production_id = p.production_ids[:1].id

    # Inherit addons/purchase_stock/models/purchase.py:PurchaseOrderLine
    def _prepare_purchase_order_line_from_procurement(
        self, product_id, product_qty, product_uom, company_id, values, po
    ):
        res = super()._prepare_purchase_order_line_from_procurement(
            product_id, product_qty, product_uom, company_id, values, po
        )
        if "production_id" in values:
            res["production_ids"] = [(6, 0, values["production_id"].ids)]
        if "bom_line_id" in values:
            res["bom_line_id"] = values["bom_line_id"].id
        return res
