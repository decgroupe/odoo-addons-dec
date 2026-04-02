# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.tests.common import TransactionCase


class TestSoftwareLicenseLegacy(TransactionCase):
    """Tests for software_license_legacy module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.Application = cls.env["software.application"]
        cls.License = cls.env["software.license"]
        cls.Hardware = cls.env["software.license.hardware"]
        cls.Feature = cls.env["software.license.feature"]
        cls.application = cls.Application.create(
            {"name": "TestApp Legacy", "type": "inhouse"}
        )
        cls.property_system = cls.env.ref(
            "software_license_legacy.feature_property_system"
        )
        cls.value_classic = cls.env.ref(
            "software_license_legacy.feature_value_system_classic"
        )
        cls.value_cave = cls.env.ref(
            "software_license_legacy.feature_value_system_cave"
        )
        cls.value_rift = cls.env.ref(
            "software_license_legacy.feature_value_system_rift"
        )
        cls.value_vive = cls.env.ref(
            "software_license_legacy.feature_value_system_vive"
        )

    def _create_license(self, serial):
        """Create a basic software.license record."""
        return self.License.create(
            {
                "serial": serial,
                "application_id": self.application.id,
            }
        )

    def _add_system_feature(self, license_rec, value):
        """Add a system feature with the given value to a license."""
        return self.Feature.create(
            {
                "license_id": license_rec.id,
                "sequence": len(license_rec.feature_ids) + 1,
                "property_id": self.property_system.id,
                "value_id": value.id,
            }
        )

    def test_01_compute_main_hardware(self):
        """main_hardware_id is set from the first hardware entry."""
        license_rec = self._create_license("TEST-LEGACY-001")
        self.assertFalse(license_rec.main_hardware_id)
        hw = self.Hardware.create(
            {"license_id": license_rec.id, "name": "aa:bb:cc:dd:ee:01"}
        )
        license_rec.invalidate_recordset()
        self.assertEqual(license_rec.main_hardware_id, hw)

    def test_02_compute_main_hardware_name(self):
        """main_hardware_name is the name of the first hardware."""
        license_rec = self._create_license("TEST-LEGACY-002")
        self.Hardware.create(
            {"license_id": license_rec.id, "name": "aa:bb:cc:dd:ee:02"}
        )
        license_rec.invalidate_recordset()
        self.assertEqual(license_rec.main_hardware_name, "aa:bb:cc:dd:ee:02")

    def test_03_compute_system_classic(self):
        """system_classic is True when a classic feature is linked."""
        license_rec = self._create_license("TEST-LEGACY-003")
        self.assertFalse(license_rec.system_classic)
        self._add_system_feature(license_rec, self.value_classic)
        license_rec.invalidate_recordset()
        self.assertTrue(license_rec.system_classic)
        self.assertFalse(license_rec.system_cave)
        self.assertFalse(license_rec.system_rift)
        self.assertFalse(license_rec.system_vive)

    def test_04_compute_system_cave(self):
        """system_cave is True when a cave feature is linked."""
        license_rec = self._create_license("TEST-LEGACY-004")
        self._add_system_feature(license_rec, self.value_cave)
        license_rec.invalidate_recordset()
        self.assertFalse(license_rec.system_classic)
        self.assertTrue(license_rec.system_cave)
        self.assertFalse(license_rec.system_rift)
        self.assertFalse(license_rec.system_vive)

    def test_05_compute_system_rift(self):
        """system_rift is True when a rift feature is linked."""
        license_rec = self._create_license("TEST-LEGACY-005")
        self._add_system_feature(license_rec, self.value_rift)
        license_rec.invalidate_recordset()
        self.assertFalse(license_rec.system_classic)
        self.assertFalse(license_rec.system_cave)
        self.assertTrue(license_rec.system_rift)
        self.assertFalse(license_rec.system_vive)

    def test_06_compute_system_vive(self):
        """system_vive is True when a vive feature is linked."""
        license_rec = self._create_license("TEST-LEGACY-006")
        self._add_system_feature(license_rec, self.value_vive)
        license_rec.invalidate_recordset()
        self.assertFalse(license_rec.system_classic)
        self.assertFalse(license_rec.system_cave)
        self.assertFalse(license_rec.system_rift)
        self.assertTrue(license_rec.system_vive)

    def test_07_create_with_system_classic(self):
        """create() with system_classic=True auto-creates the feature."""
        license_rec = self.License.create(
            {
                "serial": "TEST-LEGACY-007",
                "application_id": self.application.id,
                "system_classic": True,
            }
        )
        self.assertEqual(len(license_rec.feature_ids), 1)
        feature = license_rec.feature_ids[0]
        self.assertEqual(feature.property_id, self.property_system)
        self.assertEqual(feature.value_id, self.value_classic)
        self.assertTrue(license_rec.system_classic)

    def test_08_create_with_system_cave(self):
        """create() with system_cave=True auto-creates the feature."""
        license_rec = self.License.create(
            {
                "serial": "TEST-LEGACY-008",
                "application_id": self.application.id,
                "system_cave": True,
            }
        )
        self.assertEqual(len(license_rec.feature_ids), 1)
        feature = license_rec.feature_ids[0]
        self.assertEqual(feature.value_id, self.value_cave)
        self.assertTrue(license_rec.system_cave)

    def test_09_create_with_main_hardware_name(self):
        """create() with main_hardware_name auto-creates the hardware record."""
        license_rec = self.License.create(
            {
                "serial": "TEST-LEGACY-009",
                "application_id": self.application.id,
                "main_hardware_name": "aa:bb:cc:dd:ee:09",
            }
        )
        self.assertTrue(license_rec.hardware_ids)
        self.assertEqual(license_rec.main_hardware_id.name, "aa:bb:cc:dd:ee:09")

    def test_10_form_view_fields(self):
        """Expected fields are present in the combined form view arch."""
        view_info = self.env["software.license"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("main_hardware_id", field_names)
        self.assertIn("main_hardware_name", field_names)
        self.assertIn("main_hardware_dongle_identifier", field_names)
        self.assertIn("system_classic", field_names)
        self.assertIn("system_cave", field_names)
        self.assertIn("system_rift", field_names)
        self.assertIn("system_vive", field_names)

    def test_11_list_view_fields(self):
        """Expected fields are present in the combined list view arch."""
        view_info = self.env["software.license"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("system_classic", field_names)
        self.assertIn("system_cave", field_names)
        self.assertIn("system_rift", field_names)
        self.assertIn("system_vive", field_names)

    def test_12_search_view_fields(self):
        """Dongle groupby filter is present in the combined search view arch."""
        view_info = self.env["software.license"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"])
        filter_names = [el.get("name") for el in arch.iter("filter")]
        self.assertIn("groupby_dongle_identifier", filter_names)
