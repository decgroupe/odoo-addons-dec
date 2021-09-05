# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import re

from odoo import fields, models, api, _
from odoo.osv import expression


class SoftwareLicenseFeatureValue(models.Model):
    _name = 'software.license.feature.value'
    _description = 'Value for a feature of a software license'

    property_id = fields.Many2one(
        comodel_name='software.license.feature.property',
        string='Feature',
        required=True,
    )
    name = fields.Char(
        'Name',
        required=True,
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        return record
