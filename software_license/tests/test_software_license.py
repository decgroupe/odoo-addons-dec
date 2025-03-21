# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.tests.common import TransactionCase


class TestSoftwareLicense(TransactionCase):
    """ """

    def setUp(self):
        super().setUp()
        self.application_model = self.env["software.application"]
        self.software_license = self.env["software.license"]
        self.software_license_hardware = self.env["software.license.hardware"]

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
        hardware_id = fitness_lic1.activate("9d:24:26:52:12:81")
        self.assertEqual(len(fitness_lic1.hardware_ids), 3)
        added_hardware_id = fitness_lic1.hardware_ids - current_hardware_ids
        self.assertTrue(added_hardware_id)
        self.assertEqual(added_hardware_id.name, "9d:24:26:52:12:81")
        self.assertEqual(added_hardware_id, hardware_id)
        # test activation with same hardware
        hardware_id = fitness_lic1.activate("9d:24:26:52:12:81")
        self.assertFalse(hardware_id)
        self.assertFalse(hardware_id.exists())

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
        newage_lic3 = newage_lic2.copy({"serial": "TEST03bis"})
        self.assertEqual(newage_lic3.serial, "TEST03bis")
        self.assertEqual(newage_lic3.display_name, "[New Age] TEST03bis")

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

    def test_06_search_license(self):
        license_ids = self.software_license.get_license_ids(
            identifier="1001", serial=False
        )
        # at least 2 licenses exists from this module
        self.assertGreaterEqual(len(license_ids), 2)
        license_ids = self.software_license.get_license_ids(
            identifier="1001", serial="0DAY-0001"
        )
        self.assertEqual(len(license_ids), 1)
        license_ids = self.software_license.get_license_ids(
            identifier=False, serial="0DAY-0001"
        )
        self.assertEqual(len(license_ids), 1)

    def test_07_search_hardware(self):
        hardware_ids = self.software_license_hardware.get_hardware_ids(hardware=False)
        self.assertFalse(hardware_ids)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c"
        )
        self.assertEqual(len(hardware_ids), 2)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c", identifier="1002"
        )
        self.assertEqual(len(hardware_ids), 1)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c", identifier="1002", serial="BG-A02"
        )
        self.assertEqual(len(hardware_ids), 1)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c", serial="BG-A02"
        )
        self.assertEqual(len(hardware_ids), 1)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c", identifier="1001", serial="0DAY-0002"
        )
        self.assertEqual(len(hardware_ids), 1)
        hardware_ids = self.software_license_hardware.get_hardware_ids(
            hardware="11:ec:09:af:b6:8c", serial="0DAY-0002"
        )
        self.assertEqual(len(hardware_ids), 1)

    def test_08_device_info(self):
        fitness_lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        # legacy (telemetry was params)
        hardware_id = fitness_lic1.activate(
            "device_uuid_1",
            info="""{
                "params": {
                    "NetworkInformation": {
                        "DomainName": "ad.readymat.com",
                        "HostName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        self.assertEqual(hardware_id.device_name, "PC-ReadyMat1")
        self.assertEqual(hardware_id.device_domain, "ad.readymat.com")
        self.assertEqual(hardware_id.device_fqdn, "PC-ReadyMat1.ad.readymat.com")
        # full
        hardware_id = fitness_lic1.activate(
            "device_uuid_2",
            info="""{
                "telemetry": {
                    "NetworkInformation": {
                        "DomainName": "ad.readymat.com",
                        "HostName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        self.assertEqual(hardware_id.device_name, "PC-ReadyMat1")
        self.assertEqual(hardware_id.device_domain, "ad.readymat.com")
        self.assertEqual(hardware_id.device_fqdn, "PC-ReadyMat1.ad.readymat.com")
        # no domain
        hardware_id = fitness_lic1.activate(
            "device_uuid_3",
            info="""{
                "telemetry": {
                    "NetworkInformation": {
                        "HostName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        self.assertEqual(hardware_id.device_name, "PC-ReadyMat1")
        self.assertEqual(hardware_id.device_domain, False)
        self.assertEqual(hardware_id.device_fqdn, "PC-ReadyMat1")
        # no network information
        hardware_id = fitness_lic1.activate(
            "device_uuid_4",
            info="""{
                "telemetry": {
                    "NetworkInformation": {},
                    "SystemInfo": {
                        "deviceName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        # empty telemetry and missing `SystemInfo` node
        hardware_id = fitness_lic1.activate(
            "device_uuid_5",
            info="""{
                "telemetry": {
                    "NetworkInformation": {}
                }
            }""",
        )
        self.assertEqual(hardware_id.device_name, False)
        self.assertEqual(hardware_id.device_domain, False)
        self.assertEqual(hardware_id.device_fqdn, False)
        # partial network information
        hardware_id = fitness_lic1.activate(
            "device_uuid_6",
            info="""{
                "telemetry": {
                    "NetworkInformation": {
                        "DomainName": "ad.readymat.com"
                    },
                    "SystemInfo": {
                        "deviceName": "PC-ReadyMat1"
                    }
                }
            }""",
        )
        self.assertEqual(hardware_id.device_name, "PC-ReadyMat1")
        self.assertEqual(hardware_id.device_domain, "ad.readymat.com")
        self.assertEqual(hardware_id.device_fqdn, "PC-ReadyMat1.ad.readymat.com")
        # testing get_hardwares_dict
        hardwares_dict = fitness_lic1.get_hardwares_dict()
        self.assertEqual(len(hardwares_dict), 8)
        self.assertIn("6a:32:bb:7f:36:14", hardwares_dict)
        self.assertIn("13:bd:17:6b:03:46", hardwares_dict)
        self.assertIn("device_uuid_1", hardwares_dict)
        self.assertIn("device_uuid_2", hardwares_dict)
        self.assertIn("device_uuid_3", hardwares_dict)
        self.assertIn("device_uuid_4", hardwares_dict)
        self.assertIn("device_uuid_5", hardwares_dict)
        self.assertIn("device_uuid_6", hardwares_dict)
        hardwares_dict = fitness_lic1.get_hardwares_dict(filter_names=["device_uuid_1"])
        self.assertEqual(len(hardwares_dict), 1)
        self.assertIn("device_uuid_1", hardwares_dict)

    def test_09_license_from_partner(self):
        # Azure Interior
        az_id = self.env.ref("base.res_partner_12")
        # Azure Interior, Brandon Freeman
        bf_id = self.env.ref("base.res_partner_address_15")
        # Azure Interior, Nicole Ford
        nf_id = self.env.ref("base.res_partner_address_16")
        # Azure Interior, Colleen Diaz
        cd_id = self.env.ref("base.res_partner_address_28")
        # check assigned licenses count for each partner
        az_license_ids = self.software_license.search([("partner_id", "=", az_id.id)])
        self.assertEqual(len(az_license_ids), 0)
        bf_license_ids = self.software_license.search([("partner_id", "=", bf_id.id)])
        self.assertEqual(len(bf_license_ids), 2)
        nf_license_ids = self.software_license.search([("partner_id", "=", nf_id.id)])
        self.assertEqual(len(nf_license_ids), 1)
        cd_license_ids = self.software_license.search([("partner_id", "=", cd_id.id)])
        self.assertEqual(len(cd_license_ids), 0)
        all_license_ids = (
            az_license_ids + bf_license_ids + nf_license_ids + cd_license_ids
        )
        # check license count from partner's form view
        self.assertEqual(all_license_ids, az_id.license_ids)
        self.assertEqual(all_license_ids, bf_id.license_ids)
        self.assertEqual(all_license_ids, nf_id.license_ids)
        self.assertEqual(all_license_ids, cd_id.license_ids)
        # will now consider Azure Interior is no more a company
        az_id.is_company = False
        self.assertEqual(all_license_ids, az_id.license_ids)
        self.assertEqual(bf_license_ids, bf_id.license_ids)
        self.assertEqual(nf_license_ids, nf_id.license_ids)
        self.assertEqual(cd_license_ids, cd_id.license_ids)

