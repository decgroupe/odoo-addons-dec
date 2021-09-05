# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models, api


class RefPack(models.Model):
    """ Description """

    _name = 'ref.pack'
    _description = 'Pack'
    _rec_name = 'name'

    product_id = fields.Many2one(
        'product.template',
        'Product',
        required=True,
    )
    name = fields.Char(
        related='product_id.name',
        string='Name',
    )
    default_code = fields.Char(
        related='product_id.default_code',
        string='Code',
    )
    public_code = fields.Char(
        related='product_id.public_code',
        string='Public Code',
    )
    list_price = fields.Float(
        related='product_id.list_price',
        string='Sale Price',
    )
    standard_price = fields.Float(
        related='product_id.standard_price',
        string='Cost Price',
    )
    type = fields.Selection(
        [('company', 'Company'), ('manufacturer', 'Manufacturer')],
        'Pack Type',
        required=True,
    )

    @api.model
    def create(self, values):
        product_id = values.get('product_id')
        if product_id:
            product = self.env['product.template'].browse(product_id)
            product.pack_ok = True
            product.pack_type = 'detailed'
            product.pack_component_price = 'ignored'
            product.pack_modifiable = False
            if product.sale_ok and product.purchase_ok:
                product.pack_order_type = 'all'
            elif product.sale_ok:
                product.pack_order_type = 'sale'
            elif product.purchase_ok:
                product.pack_order_type = 'purchase'
        ref_pack = super().create(values)
        return ref_pack
