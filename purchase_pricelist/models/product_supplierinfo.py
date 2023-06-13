# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2023

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    list_price = fields.Float(
        compute="_compute_list_price",
        string="List Price",
        digits="Purchase Price",
        help="List price based on seller pricelist (Purchase UoM)",
    )
    list_price_unit = fields.Float(
        compute="_compute_list_price_unit",
        string="List Price (Default UoM)",
        digits="Purchase Price",
        help="List price based on seller pricelist (Default UoM)",
    )

    def _get_list_price(self, uom_id):
        self.ensure_one()
        res = self.price  # TODO: Convert from default UoM to uom_id
        # Ignore NewId because `_compute_price_rule_get_items` use raw SQL
        if not isinstance(self.id, models.NewId):
            pricelist = self.name.property_product_pricelist_purchase
            if pricelist:
                # Product can be a template or a variant
                product_id = self.product_id or self.product_tmpl_id
                # Convert quantities to default product UoM
                qty = self.product_uom._compute_quantity(
                    self.min_qty or 1.0, product_id.uom_id
                )
                # Warning: do not use the uom_id param, always pass as a context
                # variable. Also use the get_product_price_rule instead of
                # get_product_price to check if there was a rule match.
                # Compute with Purchase UoM
                price, rule = pricelist.with_context(uom=uom_id).get_product_price_rule(
                    product=product_id,
                    quantity=qty,
                    partner=self.name,
                )
                if rule:
                    res = price
        return res

    @api.depends("price", "min_qty")
    def _compute_list_price(self):
        for rec in self:
            rec.list_price = rec._get_list_price(rec.product_uom.id)

    @api.depends("price", "min_qty")
    def _compute_list_price_unit(self):
        for rec in self:
            rec.list_price_unit = rec._get_list_price(rec.product_id.uom_id.id)
