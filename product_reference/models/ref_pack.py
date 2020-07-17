# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

class ref_pack(models.Model):
    """ Description """

    _name = 'ref.pack'
    _description = 'Pack'
    _rec_name = 'name'

    product = fields.Many2one('product.product', 'Product', required=True)
    name = fields.Char(
        related='product.name',
        string='Name',
    )
    default_code = fields.Char(
        related='product.default_code',
        string='Code',
    )
    ciel_code = fields.Char(
        related='product.ciel_code',
        string='Ciel',
    )
    list_price = fields.Float(
        related='product.list_price',
        string='Sale Price',
    )
    standard_price = fields.Float(
        related='product.standard_price',
        string='Cost Price',
    )
    type = fields.Selection(
        [('company', 'Company'), ('manufacturer', 'Manufacturer')],
        'Pack Type',
        required=True
    )
