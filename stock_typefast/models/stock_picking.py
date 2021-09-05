# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'typefast.mixin']
