# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
