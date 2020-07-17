# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import odoo.addons.decimal_precision as dp
from odoo import fields, models


class RefMarketBom(models.Model):
    _name = 'ref.market.bom'
    _description = 'Market BoM parent and children line'

    name = fields.Char(
        'Name',
        size=64,
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        'Product',
        required=True,
    )
    product_qty = fields.Float(
        'Product Qty',
        required=True,
        digits=dp.get_precision('Product UoM'),
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        'Product UOM',
        required=True,
        help=
        "UoM (Unit of Measure) is the unit of measurement for the inventory control",
        oldname='product_uom'
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Supplier',
    )
    locked_price = fields.Boolean('Locked price')
    price = fields.Float(
        'Price',
        digits=dp.get_precision('Sale Price'),
    )
    bom_lines = fields.One2many(
        'ref.market.bom',
        'bom_id',
        'BoM Lines',
    )
    bom_id = fields.Many2one(
        'ref.market.bom',
        'Parent BoM',
        ondelete='cascade',
    )
    xml_id = fields.Char(
        compute="models.Model.get_external_id",
        size=128,
        string="External ID",
        help="ID defined in xml file"
    )
    create_date = fields.Datetime(
        'Create Date',
        readonly=True,
    )
    create_uid = fields.Many2one(
        'res.users',
        'Creator',
        readonly=True,
    )
    write_date = fields.Datetime(
        'Last Write Date',
        readonly=True,
    )
    write_uid = fields.Many2one(
        'res.users',
        'Last Writer',
        readonly=True,
    )
