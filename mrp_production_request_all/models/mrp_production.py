# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2020

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
