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


class ProductPackLine(models.Model):
    _name = 'product.pack.line'
    _inherit = _name

    product_name = fields.Char(related='product_id.name')
    product_code = fields.Char(related='product_id.default_code')
    product_uom_id = fields.Many2one(
        related='product_id.uom_po_id', readonly=True
    )
    product_categ_id = fields.Many2one(related='product_id.categ_id')
