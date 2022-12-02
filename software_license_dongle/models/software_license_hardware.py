# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models
import logging
from . import tea

_logger = logging.getLogger(__name__)

try:
    from . import _key14
except ImportError as e:
    _logger.error("Please create `_key14.py`")


class SoftwareLicenseHardware(models.Model):
    _inherit = 'software.license.hardware'

    dongle_identifier = fields.Integer(
        string='Dongle ID',
        help="Unique device ID set and given by the dongle manufacturer",
    )

    @api.onchange('dongle_identifier')
    def onchange_dongle_identifier(self):
        self.ensure_one()
        vals = {
            'name': self.get_public_dongle_identifier(self.dongle_identifier)
        }
        self.update(vals)

    @api.model
    def get_public_dongle_identifier(self, dongle_identifier):
        v = [dongle_identifier, dongle_identifier]
        enc = tea.encipher(v, _key14.KEY)

        public_dongle_id = []
        for value in enc:
            public_dongle_id.append('{:02X}'.format(value & 0xffff))
            public_dongle_id.append('{:02X}'.format(value >> 16 & 0xffff))

        return '-'.join(public_dongle_id)

    @api.model
    def get_dongle_identifier(self, public_dongle_identifier):
        if not public_dongle_identifier:
            return 0
        parts = public_dongle_identifier.split('-')

        if len(parts) != 4:
            return 0

        p1 = int(parts[0], 16) + (int(parts[1], 16) << 16)
        p2 = int(parts[2], 16) + (int(parts[3], 16) << 16)

        v = [p1, p2]
        dec = tea.decipher(v, _key14.KEY)
        if dec[0] == dec[1]:
            return dec[0]
        else:
            return 0

    def _prepare_export_vals(self, include_license_data=True):
        res = super()._prepare_export_vals(include_license_data)
        res['dongle_identifier'] = self.dongle_identifier
        return res
