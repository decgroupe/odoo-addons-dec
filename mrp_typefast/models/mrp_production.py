# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import models


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'typefast.mixin']
