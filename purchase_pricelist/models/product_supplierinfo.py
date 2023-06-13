# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2023

from odoo import api, fields, models


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    list_price = fields.Float(
        compute="_compute_list_price",
        string="List Price",
        digits="Purchase Price",
        help="List price based on seller pricelist",
    )

    @api.depends("price", "min_qty")
    def _compute_list_price(self):
        for rec in self:
            rec.list_price = rec.price
            # Ignore NewId because `_compute_price_rule_get_items` use raw SQL
            if isinstance(rec.id, models.NewId):
                continue
            pricelist = rec.name.property_product_pricelist_purchase
            if pricelist:
                # Product can be a template or a variant
                product_id = rec.product_id or rec.product_tmpl_id
                # Convert quantities to default product UoM
                qty = rec.product_uom._compute_quantity(
                    rec.min_qty or 1.0, product_id.uom_id
                )
                # Warning: do not use the uom_id param, always pass as a context
                # variable. Also use the get_product_price_rule instead of 
                # get_product_price to check if there was a rule match.
                price, rule = pricelist.with_context(
                    uom=rec.product_uom.id
                ).get_product_price_rule(
                    product=product_id,
                    quantity=qty,
                    partner=rec.name,
                    # uom_id=rec.product_uom.id,
                )
                if rule:
                    rec.list_price = price
