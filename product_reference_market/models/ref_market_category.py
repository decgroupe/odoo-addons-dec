# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefMarketCategory(models.Model):
    """ Description """

    _name = 'ref.market.category'
    _description = 'Market Category'
    _rec_name = 'description'
    _order = 'sequence'

    prefix = fields.Char(
        'Prefix',
        size=6,
        required=True,
    )
    description = fields.Char(
        'Description',
        size=128,
        required=True,
    )
    sequence = fields.Integer(
        'Position',
        required=True,
    )
