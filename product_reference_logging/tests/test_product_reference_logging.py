# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestProductReferenceLoggingCommon


class TestProductReferenceLogging(TestProductReferenceLoggingCommon):
    """Tests for product_reference_logging module."""

    def test_01_create_ref_log(self):
        """Verify that a ref.log record can be created with required fields."""
        log = self.RefLog.create(
            {
                "operation": "Test operation",
                "username": "testuser",
                "localcomputername": "testpc",
                "localusername": "localtest",
                "ipaddress": "127.0.0.1",
            }
        )
        self.assertEqual(log.operation, "Test operation")
        self.assertEqual(log.username, "testuser")
        self.assertEqual(log.localcomputername, "testpc")
        self.assertEqual(log.localusername, "localtest")
        self.assertEqual(log.ipaddress, "127.0.0.1")
        self.assertTrue(log.datetime)

    def test_02_list_view_fields(self):
        """Check that expected fields are present in the combined list view arch."""
        view_info = self.RefLog.get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("username", field_names)
        self.assertIn("operation", field_names)
        self.assertIn("localcomputername", field_names)
        self.assertIn("ipaddress", field_names)
        self.assertIn("datetime", field_names)
