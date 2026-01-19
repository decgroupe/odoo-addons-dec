# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models
from odoo.tools import float_compare


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # was `seller_info_id`
    main_seller_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Main Vendor",
        compute="_compute_main_seller_id",
    )
    # use `compute` since `related` requires a stored field
    seller_delay = fields.Integer(
        compute="_compute_main_seller_id",
    )
    seller_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_main_seller_id",
    )
    seller_product_code = fields.Char(
        compute="_compute_main_seller_id",
    )
    seller_product_name = fields.Char(
        compute="_compute_main_seller_id",
    )

    def _prepare_sellers(self, params=False):
        # Copy from `product.product`.`_prepare_sellers`
        sellers = self.seller_ids._get_filtered_supplier(self.env.company, self, params)
        return sellers.sorted(lambda s: (s.sequence, -s.min_qty, s.price, s.id))

    def _get_filtered_sellers(
        self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False
    ):
        # Copy from `product.product`.`_get_filtered_sellers`
        self.ensure_one()
        if not date:
            date = fields.Date.context_today(self)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )

        sellers_filtered = self._prepare_sellers(params)
        sellers = self.env["product.supplierinfo"]
        for seller in sellers_filtered:
            # Set quantity in UoM of seller
            quantity_uom_seller = quantity
            if quantity_uom_seller and uom_id and uom_id != seller.product_uom:
                quantity_uom_seller = uom_id._compute_quantity(
                    quantity_uom_seller, seller.product_uom
                )

            if seller.date_start and seller.date_start > date:
                continue
            if seller.date_end and seller.date_end < date:
                continue
            if partner_id and seller.partner_id not in [
                partner_id,
                partner_id.parent_id,
            ]:
                continue
            if (
                quantity is not None
                and float_compare(
                    quantity_uom_seller, seller.min_qty, precision_digits=precision
                )
                == -1
            ):
                continue
            if seller.product_tmpl_id and seller.product_tmpl_id != self:
                continue
            sellers |= seller
        return sellers

    @api.depends(
        "seller_ids.partner_id.active",
        "seller_ids.sequence",
        "seller_ids.min_qty",
        "seller_ids.price",
        "seller_ids.company_id",
        "seller_ids.product_tmpl_id",
        "seller_ids.date_start",
        "seller_ids.date_end",
        "seller_ids.delay",
    )
    @api.depends_context("company")
    def _compute_main_seller_id(self):
        for product in self:
            sellers = product._get_filtered_sellers(quantity=None).sorted("price")
            product.main_seller_id = fields.first(sellers)
            product.seller_delay = product.main_seller_id.delay
            product.seller_id = product.main_seller_id.partner_id
            product.seller_product_code = product.main_seller_id.product_code
            product.seller_product_name = product.main_seller_id.product_name
