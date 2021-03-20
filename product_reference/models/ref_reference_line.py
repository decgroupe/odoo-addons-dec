# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError

AUTO_INC_CHAR = '#'

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
    value = fields.Char('Value', )
    sequence = fields.Integer(
        'Position',
        required=True,
    )
    property_fixed = fields.Boolean(related='property_id.fixed', )

    @api.model
    def create(self, vals):
        property_id = self.env['ref.property'].browse(vals.get('property_id'))
        if property_id.fixed:
            if not vals.get('attribute_id'):
                raise UserError(
                    _('Missing attribute for property {} : {}').format(
                        vals.get('sequence', 0), property_id.name
                    )
                )
        else:
            if not vals.get('value'):
                raise UserError(
                    _('Missing value for property {} : {}').format(
                        vals.get('sequence', 0), property_id.name
                    )
                )
        line_id = super().create(vals)
        return line_id

    @api.onchange('value')
    def onchange_value(self):
        self.ensure_one()
        if not self.property_fixed:
            self.value = self.property_id.validate_value(self.value)
