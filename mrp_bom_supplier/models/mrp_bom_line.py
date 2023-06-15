# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    landmark = fields.Char("Landmark")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
    )
    seller_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Seller",
        compute="_compute_supplier_info",
    )
    delay = fields.Integer(
        string="Delay",
        compute="_compute_delay",
        inverse="_inverse_delay",
        help="Produce lead time in days if the product have to be "
        "manufactured or delivery lead time in days if the product have to "
        "be purchased.",
    )

    def _get_supplierinfo(self):
        """Given a BoM line, return the supplierinfo that matches
        with product and partner, if exist"""
        self.ensure_one()
        supplier_id = self.partner_id
        if not supplier_id:
            supplier_id = self.product_id.main_seller_id.name
        seller_id = self.product_id.with_context(
            uom=self.product_uom_id.id
        )._select_seller(partner_id=supplier_id, quantity=self.product_qty)
        return seller_id

    @api.depends("partner_id", "product_uom_id", "product_qty")
    def _compute_supplier_info(self):
        for rec in self:
            rec.seller_id = rec._get_supplierinfo()

    @api.depends("product_id.supply_method", "product_id.procure_method", "seller_id")
    def _compute_delay(self):
        for rec in self:
            if rec.product_id.procure_method == "make_to_order":
                if rec.product_id.supply_method == "buy":
                    rec.delay = rec.seller_id.delay
                elif rec.product_id.supply_method == "produce":
                    rec.delay = rec.product_id.produce_delay
            elif rec.product_id.procure_method == "make_to_stock":
                rec.delay = 0
            else:
                rec.delay = 0

    def _inverse_delay(self):
        for rec in self:
            if rec.product_id.procure_method == "make_to_order":
                if rec.product_id.supply_method == "buy":
                    if rec.seller_id:
                        rec.seller_id.delay = rec.delay
                elif rec.product_id.supply_method == "produce":
                    rec.product_id.produce_delay = rec.delay
