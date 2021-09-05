# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import json
import io
import base64
import logging

from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SoftwareLicenseHardware(models.Model):
    _inherit = 'software.license.hardware'

    validation_date = fields.Datetime(
        string='Validation Date',
        default=fields.Datetime.now,
        required=True,
    )
    validity_days = fields.Integer(
        string="Validity (Days)",
        default=2,
        required=True,
        help="The license file data can be used to internally validate an "
        "activation until this delay is reached. After this, a new validation "
        "will be required to continue using the application.",
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.license_id._check_max_allowed_hardware()
        record.license_id._check_expiration_date()
        return record

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec.license_id._check_max_allowed_hardware()
            rec.license_id._check_expiration_date()
        return res

    def _prepare(self, include_license_data=True):
        if include_license_data:
            res = self.license_id._prepare()
        else:
            res = {}
        res.update(
            {
                'hardware_identifier': self.name,
                'dongle_identifier': self.dongle_identifier,
                'date': fields.Datetime.to_string(self.validation_date),
                'validity_days': self.validity_days,
            }
        )
        return res

    @api.multi
    def get_license_string(self):
        self.ensure_one()
        self.validation_date = fields.datetime.now()

        # Create a header to help identify this license file when opening it
        # with a text editor
        lic_file = [
            '# {0} License (id: {1})'.format(
                self.license_id.application_id.name,
                self.license_id.application_id.identifier,
            )
        ]

        # Base data
        base = self._prepare()
        # Convert python dict to json string
        base_string = json.dumps(base)
        # Ensure padding of 16 byte boundary
        while len(base_string) % 16 != 0:
            base_string = base_string + '\n'
        # Convert json string to byte data
        data = base_string.encode("utf-8")

        key = RSA.import_key(self.license_id.application_id.public_key)
        session_key = get_random_bytes(16)

        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key
        # - EAX mode is not supported by .net 4
        # - CFB mode is not supported by .netcore 2
        # - ECB mode has known vulnerabilities
        cipher_aes = AES.new(session_key, AES.MODE_CBC)
        ciphertext = cipher_aes.encrypt(data)

        f = io.BytesIO()
        for x in (enc_session_key, cipher_aes.iv, ciphertext):
            f.write(x)
        f.seek(0)
        stream_length = f.getbuffer().nbytes
        # Convert encrypted binary content to base64 string
        lic_file.append(base64.encodebytes(f.read(stream_length)).decode())
        f.close()

        # Return a ready to use license string to write as a file
        return '\n'.join(lic_file)
