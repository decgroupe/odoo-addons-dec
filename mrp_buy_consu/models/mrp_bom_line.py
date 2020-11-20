# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models, _


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_small_supply = fields.Boolean(
        related='product_id.small_supply',
        readonly=True,
    )
    product_type = fields.Selection(
        related='product_id.type',
        readonly=True,
    )
    product_is_consumable = fields.Boolean(related='product_id.is_consumable', )

    buy_consumable = fields.Boolean(
        string='Buy',
        help="Used to force buying a consumable product.",
        oldname='buy_consu',
    )
