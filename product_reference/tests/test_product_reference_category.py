# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026


from .common import TestProductReferenceCommon


class TestProductReferenceCategory(TestProductReferenceCommon):
    """Test the product reference module."""

    def setUp(self):
        super().setUp()

    def test_01_category(self):
        category_id = self.RefCategory.create(
            {"code": "TEST_CAT", "name": "Test category"}
        )
        self.assertEqual(category_id.code, "TEST_CAT")
        self.assertEqual(category_id.name, "Test category")
        self.assertEqual(category_id.display_name, "[TEST_CAT] Test category")

        # seach by name
        self.assertNameSearch(category_id, "Test category", "[TEST_CAT] Test category")
        # search by code
        self.assertNameSearch(category_id, "TEST_CAT", "[TEST_CAT] Test category")
        # search by complete name
        self.assertNameSearch(
            category_id, "[TEST_CAT] Test category", "[TEST_CAT] Test category"
        )
