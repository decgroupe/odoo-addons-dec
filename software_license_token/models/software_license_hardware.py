# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

import base64
import io
import json

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SoftwareLicenseHardware(models.Model):
    _inherit = "software.license.hardware"

    validation_date = fields.Datetime(
        string="Validation Date",
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

    def write(self, vals):
        res = super().write(vals)
        license_ids = self.mapped("license_id")
        if license_ids and not self.env.context.get("bypass_license_checks", False):
            license_ids._check_max_allowed_hardware()
            license_ids._check_expiration_date()
        return res

    def _prepare_export_vals(self, include_license_data=True):
        res = super()._prepare_export_vals(include_license_data)
        res.update(
            {
                "date": fields.Datetime.to_string(self.validation_date),
                "validity_days": self.validity_days,
                "validation_expiration_date": fields.Datetime.to_string(
                    self._get_validation_expiration_date()
                ),
            }
        )
        return res

    def _get_validation_expiration_date(self):
        self.ensure_one()
        expiration_date = self.validation_date + relativedelta(days=self.validity_days)
        if self.license_id.expiration_date:
            expiration_date = min(expiration_date, self.license_id.expiration_date)
        return expiration_date

    def get_license_string(self):
        """Validate now and generate an updated license string (with encrypted data)"""
        self.ensure_one()
        self.validation_date = fields.datetime.now()

        # create a header to help identify this license file when opening it
        # with a text editor
        lic_file = [
            "# {0} License (id: {1})".format(
                self.license_id.application_id.name,
                self.license_id.application_id.identifier,
            )
        ]

        # base data
        base = self._prepare_export_vals()
        # convert python dict to json string
        base_string = json.dumps(base)
        # ensure padding of 16 byte boundary
        while len(base_string) % 16 != 0:
            base_string = base_string + "\n"
        # convert json string to byte data
        data = base_string.encode("utf-8")

        # append encrypted data only if the application owns a public key
        if self.license_id.application_id.public_key:

            key = RSA.import_key(self.license_id.application_id.public_key)
            session_key = get_random_bytes(16)

            # encrypt the session key with the public RSA key
            cipher_rsa = PKCS1_OAEP.new(key)
            enc_session_key = cipher_rsa.encrypt(session_key)

            # encrypt the data with the AES session key
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
            # convert encrypted binary content to base64 string
            lic_file.append(base64.encodebytes(f.read(stream_length)).decode())
            f.close()
        else:
            lic_file.append(base64.b64encode(data).decode())

        # Return a ready to use license string to write as a file
        return "\n".join(lic_file)
