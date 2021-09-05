# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = "id desc"
