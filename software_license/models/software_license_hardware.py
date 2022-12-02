# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models


class SoftwareLicenseHardware(models.Model):
    _name = 'software.license.hardware'
    _description = 'License Hardware'
    _order = 'id desc'

    license_id = fields.Many2one(
        'software.license',
        'License',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        required=True,
        string="Identifier",
    )
    info = fields.Text('Informations')

    def _prepare_export_vals(self, include_license_data=True):
        if include_license_data:
            res = self.license_id._prepare_export_vals()
        else:
            res = {}
        res['hardware_identifier'] = self.name
        return res
