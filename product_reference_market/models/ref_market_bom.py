# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models, api


class RefMarketBom(models.Model):
    _name = "ref.market.bom"
    _description = "Market BoM"
    _rec_name = "product_id"

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        required=True,
    )
    product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
        store=True,
    )
    line_ids = fields.One2many(
        comodel_name="ref.market.bom.line",
        inverse_name="market_bom_id",
        string="BoM Lines",
    )
    markup_rate = fields.Float(
        string="Markup rate",
        help="Used by REF manager Market",
    )
    material_cost_factor = fields.Float(
        string="Material factor (PF)",
        help="Used by REF manager Market",
    )
    labortime = fields.Float(
        string="Labor Time",
        compute="_compute_labortime",
        help="Labor hour(s) computed from BoM",
        digits=(16, 2),
    )

    def _compute_labortime(self):
        labor_service_ids = self.get_labortime_services()
        for rec in self:
            rec.labortime = 0
            for line_id in rec.line_ids:
                if line_id.product_id in labor_service_ids:
                    rec.labortime += line_id._convert_qty_to_hours()

    @api.model
    def get_default_products(self):
        """Return a list of products/services used in the reference price
        computing window (REFManager).
        """
        return self.env["product.product"]

    @api.model
    def get_default_products_as_ids(self):
        """Convert list the RPC parsable data"""
        return [x.id for x in self.get_default_products()]

    @api.model
    def get_labortime_services(self):
        """Return a list of services used to compute the labor time"""
        return self.env["product.product"]

    @api.model
    def get_labortime_services_as_ids(self):
        """Convert list the RPC parsable data"""
        return [x.id for x in self.get_labortime_services()]
