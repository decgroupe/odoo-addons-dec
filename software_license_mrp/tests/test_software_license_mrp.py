# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests.common import TransactionCase


class TestSoftwareLicenseMrp(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()

    def test_01_license_activation(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        self.assertEqual(fitness_lic1.activation_identifier, fitness_lic1.serial)
        # test exported values (even if comes from a private function)
        lic_exported_vals = fitness_lic1._prepare_export_vals()
        self.assertEqual(lic_exported_vals["production"], False)
        # test exported values from hardware
        fitness_activation1 = self.env.ref("software_license.sl_myfitnessapp1_hw1")
        hw_exported_vals = fitness_activation1._prepare_export_vals()
        self.assertEqual(hw_exported_vals["production"], False)
