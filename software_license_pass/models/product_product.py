# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2022

from odoo import fields, models, api


class Product(models.Model):
    _inherit = "product.product"

    license_pack_id = fields.Many2one(
        comodel_name='software.license.pack',
        string='Application Pack',
        help='Pack used to generate a new Application Pass.'
    )
