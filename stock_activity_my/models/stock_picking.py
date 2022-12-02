# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2022

from odoo import models, api, fields


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'mail.activity.my.mixin']
