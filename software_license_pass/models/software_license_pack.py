# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2021

import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class SoftwareLicensePack(models.Model):
    _name = 'software.license.pack'
    _description = 'License Pack'

    product_ids = fields.One2many(
        comodel_name='product.product',
        inverse_name='license_pack_id',
        string='Products',
        readonly=True,
    )
    name = fields.Char(
        string='Name',
        translate=True,
        required=True,
    )
    line_ids = fields.One2many(
        comodel_name='software.license.pack.line',
        inverse_name='pack_id',
        string='Application Pack',
        help='Applications that are part of this pack.'
    )

    @api.multi
    def write(self, vals):
        _logger.info("Writing pack data")
        return super().write(vals)
