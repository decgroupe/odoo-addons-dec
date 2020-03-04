# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class product_pack_sale(models.Model):
    _name = 'product.pack.saleline'
    _rec_name = 'product_id'

    parent_product_id = fields.Many2one(
        'product.product', 'Parent Product', ondelete='cascade', required=True
    )
    quantity = fields.Float(required=True, default=1.0)
    product_id = fields.Many2one('product.product', 'Product', required=True)
    product_name = fields.related(
        'product_id', 'name', type='char', string='Name'
    )
    product_code = fields.related(
        'product_id', 'default_code', type='char', string='Default code'
    )
    product_uom_id = fields.related(
        'product_id',
        'uom_id',
        type='many2one',
        relation='product.uom',
        string="Default Unit Of Measure",
        readonly="1"
    )
    product_categ_id = fields.related(
        'product_id',
        'categ_id',
        type='many2one',
        relation='product.category',
        string="Category"
    )
