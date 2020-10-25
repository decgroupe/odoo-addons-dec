# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_type = fields.Selection(
        related='product_id.type',
        readonly=True,
    )
    buy_consu = fields.Boolean(
        string='Buy',
        help="Used to force buying a consumable product.",
    )
