# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from datetime import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestSoftwareLicenseToken(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.REGEX_RSA_PRIVATE_KEY = (
            r"-----BEGIN RSA PRIVATE KEY-----(.|\n)*-----END RSA PRIVATE KEY-----"
        )
        self.REGEX_RSA_PUBLIC_KEY = (
            r"-----BEGIN PUBLIC KEY-----(.|\n)*-----END PUBLIC KEY-----"
        )

    def test_01_generate_keypair(self):
        brickgame_app = self.env.ref("software_application.sa_brickgame")
        self.assertFalse(brickgame_app.private_key)
        self.assertFalse(brickgame_app.public_key)
        brickgame_app.action_generate_rsa_keypair()
        self.assertRegex(brickgame_app.private_key, self.REGEX_RSA_PRIVATE_KEY)
        self.assertRegex(brickgame_app.public_key, self.REGEX_RSA_PUBLIC_KEY)
        brickgame_app.type = "other"
        self.assertFalse(brickgame_app.private_key)
        self.assertFalse(brickgame_app.public_key)

    @freeze_time("2023-11-13 11:45:20")
    def test_02_activate_hardware(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        self.assertEqual(fitness_lic1.get_remaining_activation(), 2)
        added_hardware_id = fitness_lic1.activate("9d:24:26:52:12:81")
        self.assertEqual(fitness_lic1.get_remaining_activation(), 1)
        self.assertEqual(
            added_hardware_id.validation_date, datetime(2023, 11, 13, 11, 45, 20)
        )

    def test_03_check_max_activation(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        self.assertEqual(fitness_lic1.get_remaining_activation(), 2)
        fitness_lic1.activate("device_uuid_3/4")
        self.assertFalse(fitness_lic1.check_max_activation_reached("device_uuid_3/4"))
        self.assertFalse(fitness_lic1.check_max_activation_reached("uuid_random"))
        fitness_lic1.activate("device_uuid_4/4")
        self.assertFalse(
            fitness_lic1.check_max_activation_reached("device_uuid_4/4"),
            "Max activation reached must always return False if the device is already "
            "in the list of activated hardware.",
        )
        self.assertTrue(fitness_lic1.check_max_activation_reached("uuid_random"))
        with self.assertRaisesRegex(
            ValidationError, r"Maximum hardware identifier count reached for license"
        ), self.cr.savepoint():
            fitness_lic1.activate("device_uuid_5/4")
        # check unlimited activation
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        fitness_lic3 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "max_allowed_hardware": 0,
                "serial": "FIT_003",
            }
        )
        self.assertEqual(fitness_lic3.get_remaining_activation(), -1)
        fitness_lic4 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "max_allowed_hardware": -2,
                "serial": "FIT_004",
            }
        )
        self.assertEqual(fitness_lic4.get_remaining_activation(), -1)

    @freeze_time("2023-12-01 12:00:00")
    def test_04_check_expiration(self):
        fitness_app = self.env.ref("software_application.sa_myfitnessapp")
        fitness_lic3 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "expiration_date": "2023-12-01 11:55:00",
                "serial": "FIT_003",
            }
        )
        self.assertTrue(fitness_lic3.check_expired())
        with self.assertRaisesRegex(
            ValidationError, r"Expiration date reached"
        ), self.cr.savepoint():
            fitness_lic3.activate("my_device_uuid")
        fitness_lic4 = self.software_license.create(
            {
                "application_id": fitness_app.id,
                "expiration_date": "2023-12-01 12:05:00",
                "serial": "FIT_004",
            }
        )
        self.assertFalse(fitness_lic4.check_expired())

    @freeze_time("2023-12-01 12:00:00")
    def test_05_license_activation(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        fitness_lic1.expiration_date = fields.Datetime.now() + relativedelta(days=7)
        self.assertEqual(fitness_lic1.activation_identifier, fitness_lic1.serial)
        # test exported values (even if comes from a private function)
        lic_exported_vals = fitness_lic1._prepare_export_vals()
        self.assertEqual(lic_exported_vals["expiration_date"], "2023-12-08 12:00:00")
        # test exported values from hardware
        fitness_activation1 = self.env.ref("software_license.sl_myfitnessapp1_hw1")
        hw_exported_vals = fitness_activation1._prepare_export_vals()
        self.assertEqual(hw_exported_vals["expiration_date"], "2023-12-08 12:00:00")

    @freeze_time("2023-12-10 15:00:00")
    def test_06_license_activation_details(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        hardware_id = fitness_lic1.activate("my_device_uuid")
        _filter = ["my_device_uuid"]
        hw_data = fitness_lic1.get_hardwares_dict(_filter)
        my_data = hw_data["my_device_uuid"]
        self.assertEqual(my_data["hardware_identifier"], "my_device_uuid")
        self.assertEqual(my_data["date"], "2023-12-10 15:00:00")
        self.assertEqual(my_data["validity_days"], 2)
        self.assertEqual(my_data["validation_expiration_date"], "2023-12-12 15:00:00")
        license_string = hardware_id.get_license_string()
        # check license header (remaining data is encrypted)
        self.assertRegex(license_string, r"# MyFitnessApp License \(id: 1001\)")

    def test_07_install_mode(self):
        # in install_mode, constraints must be ignored
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        _2days_ago = fields.Datetime.now() - relativedelta(days=2)
        _1day_ago = fields.Datetime.now() - relativedelta(days=1)
        _12hours_ago = fields.Datetime.now() - relativedelta(hours=12)
        # Go back to the past to manipulate activation data
        with freeze_time(_2days_ago):
            fitness_lic1.hardware_ids.write({"validation_date": _2days_ago})
            fitness_lic1.expiration_date = _1day_ago
            fitness_lic1.hardware_ids.with_context(bypass_license_checks=True).write(
                {"validation_date": _12hours_ago}
            )
        # expiration date constraint
        with self.assertRaisesRegex(
            ValidationError, r"Expiration date reached"
        ), self.cr.savepoint():
            fitness_lic1._check_expiration_date()
        self.assertIsNone(
            fitness_lic1.with_context(install_mode=True)._check_expiration_date()
        )
        # max allowed hardware constraint
        fitness_lic1.max_allowed_hardware = 1
        with self.assertRaisesRegex(
            ValidationError, r"Maximum hardware identifier count reached for license"
        ), self.cr.savepoint():
            fitness_lic1._check_max_allowed_hardware()
        self.assertIsNone(
            fitness_lic1.with_context(install_mode=True)._check_max_allowed_hardware()
        )
