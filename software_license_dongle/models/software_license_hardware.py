# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

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
        help="Unique device ID set and given by then dongle manufacturer",
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
