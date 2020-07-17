# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _name = _inherit

    @api.depends('seller_ids')
    def _get_main_product_supplier(self):
        """Determines the main (best) product supplier for ``product``, 
        returning the corresponding ``supplierinfo`` record, or False
        if none were found. The default strategy is to select the
        supplier with the highest priority (i.e. smallest sequence).

        :param browse_record product: product to supply
        :rtype: product.supplierinfo browse_record or False
        """
        sellers = [
            (seller_info.sequence, seller_info)
            for seller_info in self.seller_ids or []
            if seller_info and isinstance(seller_info.sequence, int)
        ]
        res = sellers and sellers[0][1] or False
        return res

    @api.multi
    def _calc_seller(self):
        for product in self:
            main_supplier = product._get_main_product_supplier()
            product.seller_info_id = main_supplier and main_supplier.id or False
            product.seller_delay = main_supplier and main_supplier.delay or 1
            product.seller_id = main_supplier and main_supplier.name.id or False
            product.seller_product_code = main_supplier and main_supplier.product_code or False
            product.seller_product_name = main_supplier and main_supplier.product_name or False

    seller_info_id = fields.Many2one(
        'product.supplierinfo',
        compute=_calc_seller,
        # store=True,
    )
    seller_delay = fields.Integer(
        compute=_calc_seller,
        string='Supplier Lead Time',
        # store=True,
        help="This is the average delay in days between the purchase order \
confirmation and the reception of goods for this product and for the \
default supplier. It is used by the scheduler to order requests based \
on reordering delays."
    )
    seller_id = fields.Many2one(
        'res.partner',
        compute=_calc_seller,
        # store=True,
        string='Main Supplier',
        help="Main Supplier who has highest priority in Supplier List.",
    )
    seller_product_code = fields.Char(
        compute=_calc_seller,
        string='Vendor Product Code',
        help="Main supplier product code",
    )
    seller_product_name = fields.Char(
        compute=_calc_seller,
        string='Vendor Product Name',
        help="Main supplier product name",
    )

