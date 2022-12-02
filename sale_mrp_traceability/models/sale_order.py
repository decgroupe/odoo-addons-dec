# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

