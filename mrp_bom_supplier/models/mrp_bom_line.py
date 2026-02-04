# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    landmark = fields.Char("Landmark")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        domain="[('id', 'in', seller_partner_ids)]",
    )
    seller_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Seller",
        compute="_compute_supplier_info",
    )
    seller_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Suppliers",
        compute="_compute_seller_partners",
    )
    delay = fields.Integer(
        string="Delay",
        compute="_compute_delay",
        inverse="_inverse_delay",
        help="Produce lead time in days if the product have to be "
        "manufactured or delivery lead time in days if the product have to "
        "be purchased.",
    )

    def _compute_seller_partners(self):
        for rec in self:
            rec.seller_partner_ids = rec.product_id.seller_ids.mapped("partner_id")

    @api.depends("partner_id", "product_id", "product_uom_id", "product_qty")
    def _compute_supplier_info(self):
        """Given a BoM line, return the supplierinfo that matches
        with product and partner, if exist"""
        for rec in self:
            # `_get_supplierinfo` merged to `_compute_supplier_info`
            supplier_id = rec.partner_id
            if not supplier_id:
                supplier_id = rec.product_id.main_seller_id.partner_id
            seller_id = rec.product_id.with_context(
                uom=rec.product_uom_id.id
            )._select_seller(partner_id=supplier_id, quantity=rec.product_qty)
            rec.seller_id = seller_id

    @api.depends("product_id.supply_method", "product_id.procure_method", "seller_id")
    def _compute_delay(self):
        self.delay = 0
        for rec in self:
            # always consider that a stockable product is available immediately
            if rec.product_id.procure_method == "make_to_order":
                if rec.product_id.supply_method == "buy":
                    rec.delay = rec.seller_id.delay
                elif rec.product_id.supply_method == "produce":
                    bom_id = self.env["mrp.bom"]._bom_find(rec.product_id)[
                        rec.product_id
                    ]
                    if bom_id:
                        rec.delay = bom_id.produce_delay

    def _inverse_delay(self):
        for rec in self:
            if rec.product_id.procure_method == "make_to_order":
                if rec.product_id.supply_method == "buy":
                    if rec.seller_id:
                        rec.seller_id.delay = rec.delay
                elif rec.product_id.supply_method == "produce":
                    bom_id = self.env["mrp.bom"]._bom_find(rec.product_id)[
                        rec.product_id
                    ]
                    if bom_id:
                        bom_id.produce_delay = rec.delay
