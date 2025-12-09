# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2022

from odoo import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    url = fields.Char()
