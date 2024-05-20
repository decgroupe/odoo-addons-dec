# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024


from dateutil.relativedelta import relativedelta

import odoo.tests
from odoo import fields
from odoo.addons.software_license_portal.controllers.main import SUCCESS, ERROR
from odoo.addons.software_license_portal.tests.common import (
    TestSoftwareLicensePortalBase,
)


@odoo.tests.tagged("post_install", "-at_install")
class TestSoftwareLicensePortal(TestSoftwareLicensePortalBase):

    def setUp(self):
        super().setUp()

    def test_01_activate_validate_deactivate(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ACTIVATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 1)
        # activate hardware "device_uuid_2" using same serial "0DAY-0001"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ACTIVATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 0)
        # try activating hardware "device_uuid_3"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_3", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_TOO_MANY_ACTIVATION")
        # retry activating hardware "device_uuid_2" (already activated)
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_ALREADY_ACTIVATED_ON_HARDWARE")
        # validate "device_uuid_1"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_UPDATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 0)
        # deactivate "device_uuid_1"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")
        # validate "device_uuid_2"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_UPDATED_ON_HARDWARE")
        self.assertIn("# MyFitnessApp License (id: 1001)", res.get("license_string"))
        self.assertEqual(res.get("remaining_activation"), 1)
        # deactivate "device_uuid_2"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_2", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")

    def test_02_avd_invalid_serial(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_activate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # validate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_validate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # deactivate hardware "device_uuid_1" using serial "FAKE-SERIAL" on "MyFitnessApp"
        res = self._api_deactivate(1001, "FAKE-SERIAL", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")

    def test_03_avd_invalid_application_identifier(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # activate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_activate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # validate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_validate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")
        # deactivate hardware "device_uuid_1" using serial "0DAY-0001" on "???"
        res = self._api_deactivate(6666, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "LICENSE_NOT_FOUND")

    def test_04_validate_deactivate_before_activate(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # validate "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_validate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")
        # deactivate "device_uuid_1"
        res = self._api_deactivate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")

    def test_05_activate_validate_expired(self):
        self.authenticate("test-portal", "test-portal")
        payload = self._get_common_payload_with_telemetry()
        # change expiration date in the past
        lic1 = self.env.ref("software_license.sl_myfitnessapp1")
        for hardware_id in lic1.hardware_ids:
            hardware_id.validation_date = fields.Datetime.now() - relativedelta(days=8)
        lic1.expiration_date = fields.Datetime.now() - relativedelta(days=7)
        # activate "device_uuid_1" using serial "0DAY-0001" on "MyFitnessApp"
        res = self._api_activate(1001, "0DAY-0001", "device_uuid_1", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try validating existing hardware
        self.assertIn("6a:32:bb:7f:36:14", lic1.hardware_ids.mapped("name"))
        res = self._api_validate(1001, "0DAY-0001", "6a:32:bb:7f:36:14", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # deactivate existing hardware
        res = self._api_deactivate(1001, "0DAY-0001", "6a:32:bb:7f:36:14", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_DEACTIVATED_ON_HARDWARE")
        # try activating unknown hardware
        res = self._api_activate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try validating unknown hardware
        res = self._api_validate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_EXPIRED")
        # try deactivating unknown hardware
        res = self._api_deactivate(1001, "0DAY-0001", "abcdef", payload)
        self.assertEqual(res.get("message_id"), "SERIAL_NOT_ACTIVATED_ON_HARDWARE")

    def test_06_get_serial(self):
        self.authenticate("test-portal", "test-portal")
        res = self._api_get_serial(1001, "6a:32:bb:7f:36:14")
        self.assertEqual(res.get("serial"), "0DAY-0001")
        res = self._api_get_serial(999, "6a:32:bb:7f:36:14")
        self.assertEqual(res.get("serial"), False)
        res = self._api_get_serial(1001, "00:00:00")
        self.assertEqual(res.get("serial"), False)

    def test_07_empty_get_licenses(self):
        self.authenticate("test-portal", "test-portal")
        # test-portal user do not own any license
        res1 = self._api_get_licenses_per_hardware("6a:32:bb:7f:36:14")
        self.assertFalse(res1)
        res2 = self._api_get_licenses_per_identifier(1001)
        self.assertFalse(res2)

    def test_08_get_licenses_per_hardware(self):
        # like test_07 but retry as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        # get per hardware
        res = self._api_get_licenses_per_hardware("6a:32:bb:7f:36:14")
        self.assertEqual(len(res), 1)
        self.assertIn("0DAY-0001", res)
        # check license data content
        licdata = res["0DAY-0001"]
        self.assert_license_data_0DAY0001(licdata)
        # check hardware data content
        self.assertIn("hardwares", licdata)
        hwdata = licdata.pop("hardwares")
        self.assert_hardware_data(hwdata, "6a:32:bb:7f:36:14")

    def test_09_get_licenses_per_identifier(self):
        # like test_07 but retry as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        # get per identifier
        res = self._api_get_licenses_per_identifier(1001)
        self.assertIn("0DAY-0001", res)
        # check license data content
        licdata = res["0DAY-0001"]
        self.assert_license_data_0DAY0001(licdata)
        # check no hardware data
        self.assertNotIn("hardwares", licdata)

    def test_10_get_licenses_per_hardware_wildcard(self):
        hardwares_per_serial = {
            # owned by Azure Interior, Brandon Freeman
            "0DAY-0001": [
                "6a:32:bb:7f:36:14",
                "13:bd:17:6b:03:46",
            ],
            # owned by Azure Interior, Nicole Ford
            "BG-A02": [
                "c5:28:79:ac:8d:b1",
                "72:e8:a5:64:1c:33",
                "6a:05:82:81:94:3c",
                "8b:5e:56:27:6f:8e",
            ],
            # owned by Azure Interior, Brandon Freeman
            "BG-A03": [
                "0d:cc:49:c5:10:86",
            ],
        }
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Nicole Ford from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_16")
        self.partner_authenticate(partner_id)
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Azure Interior
        partner_id = self.env.ref("base.res_partner_12")
        self.partner_authenticate(partner_id)
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )

    def test_11_get_licenses_per_hardware_wildcard(self):
        SERIAL = "N1W9F-6U49E-RW9TL-443F4"
        hardwares_per_serial = {
            # owned by Azure Interior
            SERIAL: [
                "device_uuid_1",
            ],
        }
        # same than test_10 but also include licences from active pass
        pass_basic1 = self.env.ref("software_license_pass.pass_basic1")
        # force pass state owned by Azure Interior
        pass_basic1.state = "sent"
        newage_lic = pass_basic1.license_ids[0]
        # force license serial since it is dynamically generated from demo pass data
        newage_lic.serial = SERIAL
        self._api_activate(
            newage_lic.application_id.identifier,
            pass_basic1.serial,
            "device_uuid_1",
            self._get_common_payload_with_telemetry(),
        )
        # try as Azure Interior
        partner_id = self.env.ref("base.res_partner_12")
        self.partner_authenticate(partner_id)
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        # use wildcard
        res = self._api_get_licenses_per_hardware("*")
        self.assert_hardwares_per_serial_data(
            res,
            hardwares_per_serial,
        )

    def test_12_get_all_licenses(self):
        # try as Brandon Freeman from Azure Interior
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        res = self._api_get_licenses()
        self.assertIn("0DAY-0001", res)
        self.assertIn("BG-A02", res)
        self.assertIn("BG-A03", res)

    def test_13_get_request_info(self):
        res = self._api_get_request_info()
        self.assertIn("telemetry", res)
        self.assertIn("httprequest", res)
        self.assertIn("remote_addr", res["httprequest"])
        self.assertEqual(res["httprequest"]["remote_addr"], "127.0.0.1")

    def test_14_batch_activate_validate_deactivate(self):
        pass_prm3 = self.env.ref("software_license_pass.pass_premium3")
        # force pass state owned by Azure Interior
        pass_prm3.state = "sent"
        # store automatically generated license serial
        lic_serial1 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_newage")
        ).serial
        lic_serial2 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_calm")
        ).serial
        lic_serial3 = pass_prm3.license_ids.filtered(
            lambda lic: lic.application_id
            == self.env.ref("software_application.sa_myfitnessapp")
        ).serial
        payload = self._get_common_payload_with_telemetry()
        # use pass serial only (license serials cannot be used for AVD)
        payload["params"]["data"] = {
            "1000": "9NENW-Y2XZT-3GA9C-0CD61",  # New Age
            "1001": "9NENW-Y2XZT-3GA9C-0CD61",  # MyFitnessApp
            "2000": "9NENW-Y2XZT-3GA9C-0CD61",  # Calm
        }
        # activate fake device
        res = self._api_batch_activate("device_uuid_1", payload)
        self.assertIn("9NENW-Y2XZT-3GA9C-0CD61", res)
        actdata = res["9NENW-Y2XZT-3GA9C-0CD61"]
        self.assert_batch_av_result(
            actdata, "1000", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            actdata, "1001", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            actdata, "2000", SUCCESS, "SERIAL_ACTIVATED_ON_HARDWARE"
        )
        # get licenses (without login)
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assertIsNone(res)
        # get licenses as Ready Mat
        partner_id = self.env.ref("base.res_partner_4")
        self.partner_authenticate(partner_id)
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assertIn(lic_serial1, res)
        self.assert_license_data(
            res[lic_serial1],
            application_identifier=1000,
            application_name="New Age",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        self.assertIn(lic_serial2, res)
        self.assert_license_data(
            res[lic_serial2],
            application_identifier=2000,
            application_name="Calm",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        self.assertIn(lic_serial3, res)
        self.assert_license_data(
            res[lic_serial3],
            application_identifier=1001,
            application_name="MyFitnessApp",
            partner="Ready Mat",
            serial="9NENW-Y2XZT-3GA9C-0CD61",
            remaining_activation=7,
            pass_remaining_activation=7,
            pack="Premium",
            pass_name=pass_prm3.name,
        )
        # activate another fake devices
        res = self._api_batch_activate("device_uuid_2", payload)
        res = self._api_batch_activate("device_uuid_3", payload)
        # validate first device
        res = self._api_batch_validate("device_uuid_1", payload)
        self.assertIn("9NENW-Y2XZT-3GA9C-0CD61", res)
        valdata = res["9NENW-Y2XZT-3GA9C-0CD61"]
        self.assert_batch_av_result(
            valdata, "1000", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            valdata, "1001", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        self.assert_batch_av_result(
            valdata, "2000", SUCCESS, "SERIAL_UPDATED_ON_HARDWARE"
        )
        # get licenses as Ready Mat
        res = self._api_get_licenses_per_hardware("device_uuid_1")
        self.assert_license_data(
            res[lic_serial1],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        self.assert_license_data(
            res[lic_serial2],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        self.assert_license_data(
            res[lic_serial3],
            remaining_activation=5,
            pass_remaining_activation=5,
        )
        # deactivate first device (no payload needed)
        res = self._api_batch_deactivate("device_uuid_1", payload={})
        self.assertEqual(res["result"], SUCCESS)
        self.assertEqual(res["message_id"], "ALL_SERIALS_DEACTIVATED_ON_HARDWARE")
        # deactivate unknown device (no payload needed)
        res = self._api_batch_deactivate("device_uuid_unknown", payload={})
        self.assertEqual(res["result"], ERROR)
        self.assertEqual(res["message_id"], "HARDWARE_NOT_FOUND")
