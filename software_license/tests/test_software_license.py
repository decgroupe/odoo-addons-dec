# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests.common import TransactionCase


class TestSoftwareLicense(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]

    def test_01_create_license(self):
        newage_app = self.env.ref("software_application.sa_newage")
        newage_lic1 = self.software_license.create(
            {
                "application_id": newage_app.id,
                "type": "standard",
            }
        )
        self.assertEqual(newage_lic1.serial, "New")

    def test_02_create_license_template(self):
        calm_app = self.env.ref("software_application.sa_calm")
        self.assertFalse(calm_app.template_id)
        calm_app.action_create_license_template()
        self.assertTrue(calm_app.template_id.exists())
        self.assertEqual(calm_app.template_id.type, "template")
        # set type to `other` should detach the template
        template_id = calm_app.template_id
        calm_app.type = "other"
        self.assertTrue(template_id.exists())
        self.assertFalse(calm_app.template_id)
        self.assertEqual(calm_app.identifier, 0)

    def test_03_activate_hardware(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        current_hardware_ids = fitness_lic1.hardware_ids
        self.assertEqual(len(fitness_lic1.hardware_ids), 2)
        fitness_lic1.activate("9d:24:26:52:12:81")
        self.assertEqual(len(fitness_lic1.hardware_ids), 3)
        added_hardware_id = fitness_lic1.hardware_ids - current_hardware_ids
        self.assertTrue(added_hardware_id)
        self.assertEqual(added_hardware_id.name, "9d:24:26:52:12:81")

    def test_04_license_create_and_duplicate(self):
        newage_app = self.env.ref("software_application.sa_newage")
        newage_lic1 = self.software_license.create(
            {
                "application_id": newage_app.id,
                "type": "standard",
                "serial": "TEST03",
                "partner_id": self.env.ref("base.res_partner_address_31").id,
            }
        )
        self.assertEqual(newage_lic1.display_name, "[New Age] TEST03")
        newage_lic2 = newage_lic1.copy()
        self.assertEqual(newage_lic2.serial, "TEST03 (copy)")
        self.assertEqual(newage_lic2.display_name, "[New Age] TEST03 (copy)")

    def test_05_license_activation(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        self.assertEqual(fitness_lic1.activation_identifier, fitness_lic1.serial)
        # max activation is dumb (not implemented) in this module
        max_activation_reached = fitness_lic1.check_max_activation_reached("")
        self.assertFalse(max_activation_reached)
        # test exported values (even if comes from a private function)
        lic_exported_vals = fitness_lic1._prepare_export_vals()
        self.assertEqual(lic_exported_vals["application_identifier"], 1001)
        self.assertEqual(lic_exported_vals["application_name"], "MyFitnessApp")
        self.assertEqual(
            lic_exported_vals["partner"], "Azure Interior, Brandon Freeman"
        )
        self.assertEqual(lic_exported_vals["serial"], "0DAY-0001")
        # test exported values from hardware
        fitness_activation1 = self.env.ref("software_license.sl_myfitnessapp1_hw1")
        hw_exported_vals = fitness_activation1._prepare_export_vals()
        self.assertEqual(hw_exported_vals["application_identifier"], 1001)
        self.assertEqual(hw_exported_vals["application_name"], "MyFitnessApp")
        self.assertEqual(hw_exported_vals["partner"], "Azure Interior, Brandon Freeman")
        self.assertEqual(hw_exported_vals["serial"], "0DAY-0001")
        self.assertEqual(hw_exported_vals["hardware_identifier"], "13:bd:17:6b:03:46")
