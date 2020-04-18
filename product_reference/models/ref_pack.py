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
