# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class RefProperty(models.Model):
    """ Description """

    _name = 'ref.property'
    _description = 'Property'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Text(
        'Name',
        required=True,
    )
    format = fields.Text(
        'Format',
        required=True,
    )
    fixed = fields.Boolean('Fixed values')
    attribute_ids = fields.One2many(
        'ref.attribute',
        'property_id',
        oldname='attributes',
    )
