# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2020

from odoo import fields, models


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    date_start = fields.Date(
        'Valid From',
        copy=False,
    )
    
    date_stop = fields.Date(
        'Valid Until',
        oldname='openupgrade_legacy_10_0_date_stop',
        copy=False,
    )
