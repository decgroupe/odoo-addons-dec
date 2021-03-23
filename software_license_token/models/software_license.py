# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    expiration_date = fields.Datetime(
        string="Expiration Date",
        help="If set, then after this date it will not be possible to "
        "proceed or renew any activation.",
    )
    max_allowed_hardware = fields.Integer(
        string="Maximum Activation Count",
        default=1,
        help="If more than 1, then the number of registered hardware identifiers "
        "will not be allowed to be greater than this value.",
    )

    @api.constrains('hardware_ids')
    def _check_max_allowed_hardware(self):
        for rec in self:
            if rec.max_allowed_hardware > 0 and \
            len(rec.hardware_ids) > rec.max_allowed_hardware:
                raise ValidationError(
                    _('Maximum hardware identifier count reached')
                )

    @api.constrains('hardware_ids', 'expiration_date')
    def _check_expiration_date(self):
        for rec in self.filtered('expiration_date'):
            for hardware_id in rec.hardware_ids:
                if hardware_id.validation_date > rec.expiration_date:
                    raise ValidationError(
                        _('Expiration date reached')
                    )

    @api.multi
    def activate(self, hardware):
        self.ensure_one()
        vals = {
            'license_id': self.id,
            'name': hardware,
        }
        return self.env['software.license.hardware'].create(vals)
