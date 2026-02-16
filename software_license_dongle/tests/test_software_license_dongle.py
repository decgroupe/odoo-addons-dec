# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from unittest.mock import patch

from odoo.tests.common import TransactionCase


class TestSoftwareLicenseDongle(TransactionCase):
    """Test the software license dongle module"""

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.software_license_hardware = self.env["software.license.hardware"]

    def test_01_dongle_public_private_identifier(self):
        with patch(
            "odoo.addons.software_license_dongle.models"
            ".software_license_hardware.get_key"
        ) as get_key:
            # `get_key` is patched to have a deterministic result for the test, the
            # real key should be kept secret and not pushed to the repository
            get_key.return_value = [0x111100A1, 0x111100B2, 0x111100C3, 0x111100D4]
            # use a fixed random dongle identifier for the test, in real life it
            # should be retrieved from the dongle using a specific library provided by
            # the dongle manufacturer
            private_dongle_id = 1234567
            public_dongle_id = self.env[
                "software.license.hardware"
            ].get_public_dongle_identifier(private_dongle_id)
            # the expected public dongle id is computed with the `get_key` return value
            # and the fixed random dongle identifier using the same algorithm as in the
            # module
            self.assertEqual(public_dongle_id, "B91-2E6C-CA31-B7FA")
            # test common activation flow with the dongle identifier
            newage_app = self.env.ref("software_application.sa_newage")
            newage_app.dongle_product_id = 42
            newage_lic1 = self.software_license.create(
                {
                    "application_id": newage_app.id,
                    "type": "standard",
                }
            )
            self.assertEqual(newage_lic1.serial, "New")
            newage_lic1.activate("B91-2E6C-CA31-B7FA")
            hardware_id = newage_lic1.hardware_ids
            self.assertEqual(len(hardware_id), 1)
            self.assertEqual(hardware_id.dongle_identifier, 1234567)
            hw_exported_vals = hardware_id._prepare_export_vals()
            self.assertIn("dongle_identifier", hw_exported_vals)
            self.assertEqual(hw_exported_vals["dongle_identifier"], 1234567)
            self.assertIn("hardware_identifier", hw_exported_vals)
            self.assertEqual(
                hw_exported_vals["hardware_identifier"], "B91-2E6C-CA31-B7FA"
            )

    def test_02_application_type(self):
        """Test that the dongle product id is only set for inhouse applications"""
        newage_app = self.env.ref("software_application.sa_newage")
        self.assertEqual(newage_app.type, "inhouse")
        newage_app.dongle_product_id = 42
        newage_app.type = "other"
        self.assertEqual(newage_app.dongle_product_id, 0)
