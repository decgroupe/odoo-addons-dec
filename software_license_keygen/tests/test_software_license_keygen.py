# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests.common import TransactionCase


class TestSoftwareLicenseKeygen(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.REGEX_SERIAL = r"[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}"

    def test_01_create_license_with_serial_01(self):
        brickgame_app = self.env.ref("software_application.sa_brickgame")
        self.assertTrue(brickgame_app.auto_generate_serial)
        brickgame_lic2 = self.software_license.create(
            {
                "application_id": brickgame_app.id,
                "type": "standard",
            }
        )
        self.assertNotEqual(brickgame_lic2.serial, "New")
        self.assertRegex(brickgame_lic2.serial, self.REGEX_SERIAL)
        brickgame_lic3 = brickgame_lic2.copy()
        self.assertRegex(brickgame_lic3.serial, self.REGEX_SERIAL)
        self.assertNotEqual(brickgame_lic2.serial, brickgame_lic3.serial)

    def test_02_create_license_with_serial_01(self):
        newage_app = self.env.ref("software_application.sa_newage")
        self.assertFalse(newage_app.auto_generate_serial)
        newage_lic1 = self.software_license.create(
            {
                "application_id": newage_app.id,
                "type": "standard",
            }
        )
        self.assertEqual(newage_lic1.serial, "New")
        newage_lic1.action_generate_serial()
        self.assertRegex(newage_lic1.serial, self.REGEX_SERIAL)
        newage_lic2 = self.software_license.with_context(
            force_generate_serial=True
        ).create(
            {
                "application_id": newage_app.id,
                "type": "standard",
            }
        )
        self.assertRegex(newage_lic2.serial, self.REGEX_SERIAL)

    def test_03_auto_disable_generate_serial(self):
        brickgame_app = self.env.ref("software_application.sa_brickgame")
        self.assertEqual(brickgame_app.type, "inhouse")
        self.assertTrue(brickgame_app.auto_generate_serial)
        brickgame_app.type = "other"
        self.assertFalse(brickgame_app.auto_generate_serial)
