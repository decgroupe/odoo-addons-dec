# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    expiration_date = fields.Datetime(
        string="Expiration Date",
        track_visibility='onchange',
        help="If set, then after this date it will not be possible to "
        "proceed or renew any activation.",
    )
    max_allowed_hardware = fields.Integer(
        string="Maximum Activation Count",
        default=1,
        track_visibility='onchange',
        help="If more than 0, then the number of registered hardware "
        "identifiers will not be allowed to be greater than this value.",
    )

    @api.constrains('hardware_ids')
    def _check_max_allowed_hardware(self):
        if self.env.context.get('install_mode'):
            # Ignore constraint when loading XML data
            return
        for rec in self:
            if rec.max_allowed_hardware > 0 and \
            len(rec.hardware_ids) > rec.max_allowed_hardware:
                raise ValidationError(
                    _('Maximum hardware identifier count reached')
                )

    @api.constrains('hardware_ids', 'expiration_date')
    def _check_expiration_date(self):
        if self.env.context.get('install_mode'):
            # Ignore constraint when loading XML data
            return
        for rec in self.filtered('expiration_date'):
            for hardware_id in rec.hardware_ids:
                if hardware_id.validation_date > rec.expiration_date:
                    raise ValidationError(_('Expiration date reached'))

    def get_remaining_activation(self):
        self.ensure_one()
        if self.max_allowed_hardware <= 0:
            return -1
        else:
            return self.max_allowed_hardware - len(self.hardware_ids)

    @api.multi
    def get_hardwares_dict(self):
        self.ensure_one()
        res = {}
        for hardware_id in self.hardware_ids:
            hardware_data = hardware_id._prepare(include_license_data=False)
            # FIXME: dongle_identifier is already included in hardware_data ?
            hardware_data.update(
                {
                    'dongle_identifier': hardware_id.dongle_identifier,
                }
            )
            res[hardware_id.name] = hardware_data
        return res

    def _prepare(self, include_serial=True):
        res = {
            'application_identifier': self.application_id.identifier,
            'application_name': self.application_id.name,
            'expiration_date': fields.Datetime.to_string(self.expiration_date),
            'features': self.get_features_dict(),
            'partner': self.partner_id.display_name,
            'production': self.production_id.display_name,
        }
        if include_serial:
            res['serial'] = self.serial
        return res
