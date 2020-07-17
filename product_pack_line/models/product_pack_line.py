# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ProductPackLine(models.Model):
    _name = 'product.pack.line'
    _inherit = _name

    product_name = fields.Char(related='product_id.name')
    product_code = fields.Char(related='product_id.default_code')
    product_uom_id = fields.Many2one(
        related='product_id.uom_po_id', readonly=True
    )
    product_categ_id = fields.Many2one(related='product_id.categ_id')
