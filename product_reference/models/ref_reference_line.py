# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class RefReferenceLine(models.Model):
    """ Description """

    _name = 'ref.reference.line'
    _description = 'Reference line'
    _rec_name = 'value'
    _order = 'sequence'

    reference_id = fields.Many2one(
        'ref.reference',
        'Reference',
        required=True,
        oldname='reference',
    )
    property_id = fields.Many2one(
        'ref.property',
        'Property',
        required=True,
        oldname='property',
    )
    attribute_id = fields.Many2one(
        'ref.attribute',
        'Attribute',
    )
    value = fields.Text('Value', )
    sequence = fields.Integer(
        'Position',
        required=True,
    )
