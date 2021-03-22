# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models, api, _
from odoo.exceptions import UserError

AUTO_INC_CHAR = '#'


class SoftwareLicenseFeature(models.Model):
    _name = 'software.license.feature'
    _description = 'Feature for a software license'
    _rec_name = 'value'
    _order = 'sequence'

    sequence = fields.Integer(
        'Position',
        required=True,
    )
    license_id = fields.Many2one(
        comodel_name='software.license',
        string='License',
        required=True,
    )
    property_id = fields.Many2one(
        comodel_name='software.license.feature.property',
        string='Property',
        required=True,
    )
    value_id = fields.Many2one(
        'software.license.feature.value',
        'Value',
    )
    value = fields.Char(
        'Value',
        help="Custom value for this property, accessible only if the "
        "property is set as customizable",
    )
    customizable = fields.Boolean(
        related='property_id.customizable',
        help="Technical fields to indicate that the property is customizable",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            raise_missing_error = False
            property_id = self.env['software.license.feature.property'].browse(
                vals.get('property_id')
            )
            if not property_id.customizable:
                if not vals.get('value_id'):
                    raise_missing_error = True
            else:
                if not vals.get('value'):
                    raise_missing_error = True
            if raise_missing_error:
                raise UserError(
                    _('Missing value for property {} : {}').format(
                        vals.get('sequence', 0), property_id.name
                    )
                )
        records = super().create(vals_list)
        return records

    def _prepare_template_vals(self):
        self.ensure_one()
        return {
            'sequence': self.sequence,
            'property_id': self.property_id.id,
            'value_id': self.value_id.id,
            'value': self.value,
        }