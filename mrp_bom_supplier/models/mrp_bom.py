# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import api, fields, models, _


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char('Name')
