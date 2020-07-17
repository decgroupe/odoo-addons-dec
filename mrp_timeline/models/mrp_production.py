# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Apr 2020

from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    bom_name = fields.Char(
        'Bill of Materials Name',
        related='bom_id.name',
        readonly=True,
    )
