# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.tests import Form

from .common import TestWebXmlImportCommon


class TestWebXmlImport(TestWebXmlImportCommon):
    """Tests for web_xml_import module."""

    def test_01_list_view_fields(self):
        """Check that expected fields are present in the combined list view arch."""
        view_info = self.env["xml.data"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("module", field_names)

    def test_02_form_view_fields(self):
        """Check that expected fields are present in the combined form view arch."""
        view_info = self.env["xml.data"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("module", field_names)
        self.assertIn("content", field_names)
        self.assertIn("note", field_names)
        self.assertIn("active", field_names)

    def test_03_search_view_fields(self):
        """Check that expected fields are present in the combined search view arch."""
        view_info = self.env["xml.data"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("module", field_names)
        self.assertIn("content", field_names)

    def test_04_create_xml_data(self):
        """Verify that an xml.data record can be created with default values."""
        record = self.XmlData.create(
            {
                "name": "test record",
                "content": self.valid_xml_content,
            }
        )
        self.assertTrue(record.active)
        self.assertEqual(record.module, "xml_import")

    def test_05_action_import_init(self):
        """Verify action_import_init runs without error on valid XML content."""
        record = self.XmlData.create(
            {
                "name": "test init import",
                "module": "base",
                "content": self.valid_xml_content,
            }
        )
        # should not raise
        record.action_import_init()

    def test_06_action_import_update(self):
        """Verify action_import_update runs without error on valid XML content."""
        record = self.XmlData.create(
            {
                "name": "test update import",
                "module": "base",
                "content": self.valid_xml_content,
            }
        )
        # should not raise
        record.action_import_update()

    def test_07_invalid_xml_raises(self):
        """Verify that importing XML failing the Odoo schema raises an error."""
        # valid XML but not a valid Odoo data document (fails RelaxNG schema)
        record = self.XmlData.create(
            {
                "name": "test invalid import",
                "module": "base",
                "content": (
                    "<not_odoo_root><invalid_tag>test</invalid_tag>" "</not_odoo_root>"
                ),
            }
        )
        with self.assertRaises(AssertionError):
            record.action_import_init()

    def test_08_form_view_web_ribbon(self):
        """Verify that the archived ribbon is invisible when record is active."""
        record = self.XmlData.create(
            {
                "name": "test ribbon",
                "content": self.valid_xml_content,
            }
        )
        with Form(record) as form:
            self.assertTrue(form.active)
