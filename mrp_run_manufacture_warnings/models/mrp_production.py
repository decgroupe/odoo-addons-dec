# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
