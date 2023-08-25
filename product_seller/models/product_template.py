# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _name = _inherit

    main_seller_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        string="Main Vendor",
        compute="_compute_main_seller_id",
    )

    @api.depends(
        "seller_ids.name.active",
        "seller_ids.sequence",
        "seller_ids.min_qty",
        "seller_ids.price",
        "seller_ids.company_id",
        "seller_ids.product_id",
        "seller_ids.date_start",
        "seller_ids.date_end",
    )
    @api.depends_context("company")
    def _compute_main_seller_id(self):
        for product in self:
            sellers = product._get_sellers()
            product.main_seller_id = fields.first(sellers)

    def _get_sellers(self):
        """Returns all available sellers of a product based on some constraints.

        They are ordered and filtered like it is done in the standard 'product' addon.
        """
        self.ensure_one()
        all_sellers = self._prepare_sellers(False).filtered(
            lambda s: not s.company_id or s.company_id.id == self.env.company.id
        )
        today = fields.Date.context_today(self)
        sellers = all_sellers.filtered(
            lambda s: (
                (s.product_id == self or not s.product_id)
                and (
                    (s.date_start <= today if s.date_start else True)
                    and (s.date_end >= today if s.date_end else True)
                )
            )
        )
        if not sellers:
            sellers = all_sellers.filtered(lambda s: (s.product_tmpl_id == self))
            if not sellers:
                sellers = sellers = all_sellers.filtered(
                    lambda s: not s.product_tmpl_id
                )
        return sellers.sorted("price")

    def _calc_seller(self):
        for product in self:
            main_supplier = product.main_seller_id
            product.seller_info_id = main_supplier and main_supplier.id or False
            product.seller_delay = main_supplier and main_supplier.delay or 1
            product.seller_id = main_supplier and main_supplier.name.id or False
            product.seller_product_code = (
                main_supplier and main_supplier.product_code or False
            )
            product.seller_product_name = (
                main_supplier and main_supplier.product_name or False
            )

    seller_info_id = fields.Many2one(
        comodel_name="product.supplierinfo",
        compute=_calc_seller,
    )
    seller_delay = fields.Integer(
        compute=_calc_seller,
        string="Supplier Lead Time",
        help="This is the average delay in days between the purchase order "
        "confirmation and the reception of goods for this product and for the "
        "default supplier. It is used by the scheduler to order requests based "
        "on reordering delays.",
    )
    seller_id = fields.Many2one(
        comodel_name="res.partner",
        compute=_calc_seller,
        string="Main Supplier",
        help="Main Supplier who has highest priority in Supplier List.",
    )
    seller_product_code = fields.Char(
        compute=_calc_seller,
        string="Vendor Product Code",
        help="Main supplier product code",
    )
    seller_product_name = fields.Char(
        compute=_calc_seller,
        string="Vendor Product Name",
        help="Main supplier product name",
    )
