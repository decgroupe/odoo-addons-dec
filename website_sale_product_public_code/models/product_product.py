# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import fields, models, api


class Product(models.Model):
    _inherit = 'product.product'

