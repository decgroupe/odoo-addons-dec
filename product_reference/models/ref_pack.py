# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class RefPack(models.Model):
    """ Description """

    _name = 'ref.pack'
    _description = 'Pack'
    _rec_name = 'name'

    product_id = fields.Many2one(
        'product.template',
        'Product',
        required=True,
        oldname='product',
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
        oldname='ciel_code',
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
