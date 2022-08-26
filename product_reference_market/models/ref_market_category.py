# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from attr import field
from odoo import api, fields, models


class RefMarketCategory(models.Model):
    _name = 'ref.market.category'
    _description = 'Market Category'
    _rec_name = 'description'
    _order = 'sequence'

    prefix = fields.Char(
        string='Prefix',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    sequence = fields.Integer(
        string='Position',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('obsolete', 'Obsolete'),
            ('title', 'Title'),
        ],
        string='Status',
        default='normal',
    )
