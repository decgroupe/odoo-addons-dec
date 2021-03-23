# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2021

import string
import time
from Crypto.Hash import SHA256
from key_generator.key_generator import generate

from odoo import api, fields, models

SEPARATOR = '-'
LENGTH = 5


class SoftwareLicense(models.Model):
    _inherit = 'software.license'

    # @api.model
    # def default_get(self, fields_list):
    #     vals = super().default_get(fields_list)
    #     if not vals.get('serial'):
    #         vals['serial'] = self._generate_serial()
    #     return vals

    @api.onchange('application_id')
    def onchange_application_id(self):
        self.ensure_one()
        vals = {}
        if self.application_id.auto_generate_serial:
            vals['serial'] = self._generate_serial()
        else:
            vals['serial'] = False
        self.update(vals)

    @api.multi
    def action_generate_serial(self):
        for rec in self:
            rec.serial = rec._generate_serial()

    def _generate_serial(self):
        timestamp = time.time()
        # List of characters that will be excluded from the generator
        excluded_chars = ['O']
        # List of characters that will be used by the generator
        extras = [c for c in string.ascii_uppercase if not c in excluded_chars]
        # Generate the key using the current timestamp as the seed
        key_custom = generate(
            3,
            SEPARATOR,
            LENGTH,
            LENGTH,
            type_of_value='int',
            capital='none',
            extras=extras,
            seed=timestamp
        ).get_key().upper()

        # Generate the signature but only on a key cleared of separator char
        key_without_separator = key_custom.replace(SEPARATOR, '')
        key_signature = SHA256.SHA256Hash(key_without_separator.encode()
                                         ).hexdigest()
        # We keep only the first values of the signature as a checksum
        key_checksum = key_signature[0:LENGTH].upper()

        # The checksum is added at the end of the key
        serial = '{}{}{}'.format(key_custom, SEPARATOR, key_checksum)
        return serial

