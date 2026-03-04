# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026


from .common import TestProductReferenceCommon


class TestProductReferenceAttribute(TestProductReferenceCommon):
    """Test the product reference module."""

    def setUp(self):
        super().setUp()
        self.property_id = self.RefProperty.create(
            {
                "name": "Test property",
                "format": "NN",
                "fixed": True,
            }
        )
        self.property_id.onchange_format()

    def test_01_attribute(self):
        attribute_id = self.RefAttribute.create(
            {
                "code": "TEST_ATTR",
                "name": "Test attribute",
                "property_id": self.property_id.id,
            }
        )
        self.assertEqual(attribute_id.code, "TEST_ATTR")
        self.assertEqual(attribute_id.name, "Test attribute")
        self.assertEqual(attribute_id.display_name, "[TEST_ATTR] Test attribute")

        # seach by name
        self.assertNameSearch(
            attribute_id, "Test attribute", "[TEST_ATTR] Test attribute"
        )
        # search by code
        self.assertNameSearch(attribute_id, "TEST_ATTR", "[TEST_ATTR] Test attribute")
        # search by complete name
        self.assertNameSearch(
            attribute_id, "[TEST_ATTR] Test attribute", "[TEST_ATTR] Test attribute"
        )
