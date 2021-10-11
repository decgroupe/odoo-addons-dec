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

    def _name_get(self):
        self.ensure_one()
        res = self.name
        if self.user_has_groups('base.group_no_one'):
            res = ('%s (%s)') % (res, self.property_id.name)
        return res

    @api.multi
    @api.depends('name', 'property_id.name')
    def name_get(self):
        result = []
        for rec in self:
            name = rec._name_get()
            result.append((rec.id, name))
        return result
