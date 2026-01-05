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

    def _get_list_price(self, uom_id=False):
        self.ensure_one()
        # Product can be a template or a variant
        product_id = self.product_id or self.product_tmpl_id
        #
        # if isinstance(product_id.id, models.NewId):
        #     product_id = product_id._origin
        if uom_id:
            price_uom = self.env["uom.uom"].browse(uom_id)
        else:
            price_uom = product_id.uom_id
        res = product_id.uom_po_id._compute_price(self.price, price_uom)
        pricelist = self.partner_id.property_product_pricelist_purchase
        if pricelist:
            # Convert quantities to default product UoM
            qty = self.product_uom._compute_quantity(
                self.min_qty or 1.0, product_id.uom_id
            )
            # Use the get_product_price_rule instead of
            # get_product_price to check if there was a rule match.
            # Compute with Purchase UoM
            price, rule = pricelist.with_context(
                force_filter_supplier_id=self.partner_id
            )._get_product_price_rule(
                product=product_id,
                quantity=qty,
                uom=self.env["uom.uom"].browse(uom_id) or product_id.uom_id,
            )
            if rule:
                res = price
        return res

    @api.depends(
        "min_qty",
        "price",
        "date_start",
        "date_end",
        "discount",
        "product_id",
        "product_tmpl_id",
        "product_uom",
        "partner_id",
    )
    def _compute_list_price(self):
        # IMPORTANT: Do not merge with `_compute_list_price_unit` as both methods
        # are later used to analyze the computation graph/steps separately.
        for rec in self:
            # Price (Purchase UoM): product_uom is related to product_tmpl_id.uom_po_id
            rec.list_price = rec._get_list_price(rec.product_uom.id)

    @api.depends(
        "min_qty",
        "price",
        "date_start",
        "date_end",
        "discount",
        "product_id",
        "product_tmpl_id",
        "product_uom",
        "partner_id",
    )
    def _compute_list_price_unit(self):
        # IMPORTANT: Do not merge with `_compute_list_price` as both methods
        # are later used to analyze the computation graph/steps separately.
        for rec in self:
            # Price (Default UoM):
            rec.list_price_unit = rec._get_list_price(rec.product_id.uom_id.id)
