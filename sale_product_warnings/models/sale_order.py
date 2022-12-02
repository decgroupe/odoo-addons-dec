# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2022

from odoo import api, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
