# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    picking_id = fields.Many2one(
        'stock.picking',
        'Picking List',
        oldname='openupgrade_legacy_8_0_picking_id',
    )
