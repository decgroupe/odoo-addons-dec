# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024


import odoo.tests
from odoo.exceptions import UserError, AccessDenied
from odoo.addons.software_license_portal.tests.common import (
    TestSoftwareLicensePortalBase,
)


@odoo.tests.tagged("post_install", "-at_install")
class TestSoftwareLicensePortalMyAccount(TestSoftwareLicensePortalBase):

    def setUp(self):
        super().setUp()

    def assertLicenseTable(self, el, data):
        license_link = el.xpath(".//a")
        self.assertEqual(len(license_link), 1)
        self.assertEqual(license_link[0].text.strip(), data["serial_text"])
        self.assertEqual(license_link[0].get("href"), data["href"])
        tds = el.xpath(".//td")
        self.assertEqual(len(tds), 5)
        # owner emoji: 👷 or 🏢
        owner = tds[0].text
        self.assertIn(data["owner"], owner)
        # application text
        d = tds[2].text_content()
        application_texts = [x.strip() for x in d.split("\n") if x.strip()]
        self.assertEqual(application_texts, data["application_texts"])
        # has expiration date
        expiration_date = tds[-1].text_content().strip()
        if data["has_expiration_date"]:
            self.assertTrue(expiration_date)
        else:
            self.assertFalse(expiration_date)

    def assertPassTable(self, el, data):
        pass_link = el.xpath(".//a")
        self.assertEqual(len(pass_link), 1)
        serial = pass_link[0].text.strip()
        if data["has_serial_text"]:
            self.assertTrue(serial)
        else:
            self.assertFalse(serial)
        self.assertEqual(pass_link[0].get("href"), data["href"])
        tds = el.xpath(".//td")
        self.assertEqual(len(tds), 6)
        # owner emoji: 👷 or 🏢
        owner = tds[0].text
        self.assertIn(data["owner"], owner)
        # ref text
        ref = tds[1].text_content().strip()
        self.assertIn(data["ref"], ref)
        # pack text
        pack = tds[3].text_content().strip()
        self.assertIn(data["pack"], pack)
        # has expiration date
        expiration_date = tds[-1].text_content().strip()
        if data["has_expiration_date"]:
            self.assertTrue(expiration_date)
        else:
            self.assertFalse(expiration_date)

    def assertHardwareIdentifierTable(self, el, data):
        tds = el.xpath(".//td")
        self.assertEqual(len(tds), 4)
        # unique id
        unique_id = tds[0].text_content()
        self.assertIn(data["unique_id"], unique_id)
        # has expiration date
        last_activation_date = tds[1].text_content().strip()
        if data["has_last_activation_date"]:
            self.assertTrue(last_activation_date)
        else:
            self.assertFalse(last_activation_date)
        # form action
        action_form = el.xpath(".//form")
        self.assertEqual(len(action_form), 1)
        action_button = action_form[0].xpath("./button")
        self.assertEqual(len(action_button), 1)
        self.assertEqual(action_button[0].text.strip(), data["action_text"])
        self.assertEqual(action_form[0].get("action"), data["action_url"])
        self.assertEqual(
            action_form[0].inputs["hardware_id"].value,
            str(data["action_args"]["hardware_id"]),
        )
        self.assertEqual(
            action_form[0].inputs["license_id"].value,
            str(data["action_args"]["license_id"]),
        )

    def assertHardwareGroupTable(self, el, data):
        tds = el.xpath(".//td")
        self.assertEqual(len(tds), 3)
        # unique id
        unique_id = tds[0].text_content()
        self.assertIn(data["unique_id"], unique_id)
        # device name
        device_name = tds[1].text_content()
        self.assertIn(data["device_name"], device_name)
        # form action
        action_form = el.xpath(".//form")
        self.assertEqual(len(action_form), 1)
        action_button = action_form[0].xpath("./button")
        self.assertEqual(len(action_button), 1)
        self.assertEqual(action_button[0].text.strip(), data["action_text"])
        self.assertEqual(action_form[0].get("action"), data["action_url"])
        self.assertEqual(
            action_form[0].inputs["pass_id"].value,
            str(data["action_args"]["pass_id"]),
        )
        self.assertEqual(
            action_form[0].inputs["hardware_name"].value,
            data["action_args"]["hardware_name"],
        )

    def test_01_mylicenses(self):
        data = [
            {
                "owner": "👷",
                "serial_text": "BG-A03",
                "href": "/my/license/%d"
                % self.env.ref("software_license.sl_brickgame3").id,
                "application_texts": ["The Brick Game", "2D Arcade Game"],
                "has_expiration_date": False,
            },
            {
                "owner": "👷",
                "serial_text": "0DAY-0001",
                "href": "/my/license/%d"
                % self.env.ref("software_license.sl_myfitnessapp1").id,
                "application_texts": ["MyFitnessApp"],
                "has_expiration_date": True,
            },
        ]
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        response = self.url_open("/my/licenses")
        self.assertEqual(response.status_code, 200)
        doc = self.html_doc(response)
        for i, el in enumerate(doc.xpath("//table[@name='licenses']//tbody/tr")):
            self.assertLicenseTable(el, data[i])

    def test_02_mylicense(self):
        license_id = self.env.ref("software_license.sl_myfitnessapp1")
        data = [
            {
                "unique_id": "6a:32:bb:7f:36:14",
                "has_last_activation_date": True,
                "action_text": "Deactivate",
                "action_url": "/my/license/deactivate",
                "action_args": {
                    "hardware_id": self.env.ref(
                        "software_license.sl_myfitnessapp1_hw2"
                    ).id,
                    "license_id": license_id.id,
                },
            },
            {
                "unique_id": "13:bd:17:6b:03:46",
                "has_last_activation_date": True,
                "action_text": "Deactivate",
                "action_url": "/my/license/deactivate",
                "action_args": {
                    "hardware_id": self.env.ref(
                        "software_license.sl_myfitnessapp1_hw1"
                    ).id,
                    "license_id": license_id.id,
                },
            },
        ]
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        response = self.url_open(f"/my/license/{license_id.id}")
        self.assertEqual(response.status_code, 200)
        doc = self.html_doc(response)
        for i, el in enumerate(
            doc.xpath("//table[@name='hardware_identifiers']//tbody/tr")
        ):
            self.assertHardwareIdentifierTable(el, data[i])

    def test_03_mylicense_tour(self):
        license_id = self.env.ref("software_license.sl_brickgame3")
        self.assertEqual(len(license_id.hardware_ids), 1)
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        self.start_tour(
            "/my/licenses",
            "mylicense_tour",
            login="brandon.freeman55@example.com",
        )
        self.assertEqual(len(license_id.hardware_ids), 0)

    def test_04_mypasses(self):
        data = [
            {
                "owner": "🏢",
                "ref": "AP/240100",
                "has_serial_text": True,
                "href": "/my/pass/%d"
                % self.env.ref("software_license_pass.pass_basic1").id,
                "pack": "Basic",
                "has_expiration_date": False,
            },
        ]
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        response = self.url_open("/my/passes")
        self.assertEqual(response.status_code, 200)
        doc = self.html_doc(response)
        for i, el in enumerate(doc.xpath("//table[@name='passes']//tbody/tr")):
            self.assertPassTable(el, data[i])

    def test_05_mypass(self):
        pass_id = self.env.ref("software_license_pass.pass_premium3")
        data = [
            {
                "unique_id": "3925aab3fa0dd",
                "device_name": "PC-ReadyMat1.ad.readymat.com",
                "action_text": "Deactivate",
                "action_url": "/my/pass/deactivate",
                "action_args": {
                    "pass_id": pass_id.id,
                    "hardware_name": "3925aab3fa0dd",
                },
            },
            {
                "unique_id": "ab99c8ef7899f",
                "device_name": "PC-ReadyMat2.ad.readymat.com",
                "action_text": "Deactivate",
                "action_url": "/my/pass/deactivate",
                "action_args": {
                    "pass_id": pass_id.id,
                    "hardware_name": "ab99c8ef7899f",
                },
            },
        ]
        # Ready Mat
        partner_id = self.env.ref("base.res_partner_4")
        self.partner_authenticate(partner_id)
        response = self.url_open(f"/my/pass/{pass_id.id}")
        self.assertEqual(response.status_code, 200)
        doc = self.html_doc(response)
        for i, el in enumerate(doc.xpath("//table[@name='hardware_groups']//tbody/tr")):
            self.assertHardwareGroupTable(el, data[i])

    def test_06_mypass_tour(self):
        pass_id = self.env.ref("software_license_pass.pass_premium3")
        self.assertEqual(len(pass_id.hardware_group_ids), 2)
        # Ready Mat
        with self.assertRaisesRegex(AccessDenied, "Access Denied"), self.cr.savepoint():
            self.start_tour(
                "/my/passes",
                "mypass_tour",
                login="ready.mat28@example.com",
            )
        # Give portal access if needed
        partner_id = self.env.ref("base.res_partner_4")
        self.partner_authenticate(partner_id)
        self.start_tour(
            "/my/passes",
            "mypass_tour",
            login="ready.mat28@example.com",
        )
        self.assertEqual(len(pass_id.hardware_group_ids), 1)

    def test_07_mypass_no_hardware_tour(self):
        # Azure Interior, Brandon Freeman
        partner_id = self.env.ref("base.res_partner_address_15")
        self.partner_authenticate(partner_id)
        self.start_tour(
            "/my/passes",
            "mypass_no_hardware_tour",
            login="brandon.freeman55@example.com",
        )

