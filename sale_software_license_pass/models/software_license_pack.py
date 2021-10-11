# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SoftwareLicensePack(models.Model):
    _inherit = 'software.license.pack'

    product_ids = fields.One2many(
        comodel_name='product.product',
        inverse_name='license_pack_id',
        string='Products',
        readonly=True,
    )
