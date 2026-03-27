# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestDocumentPageCategoryName(TransactionCase):
    """Tests for document_page_category_name module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.DocumentPage = cls.env["document.page"]
        cls.root_category = cls.DocumentPage.create(
            {
                "name": "Root Category",
                "type": "category",
            }
        )
        cls.child_category = cls.DocumentPage.create(
            {
                "name": "Child Category",
                "type": "category",
                "parent_id": cls.root_category.id,
            }
        )
        cls.grandchild_category = cls.DocumentPage.create(
            {
                "name": "Grandchild Category",
                "type": "category",
                "parent_id": cls.child_category.id,
            }
        )
        cls.page = cls.DocumentPage.create(
            {
                "name": "A Page",
                "type": "content",
                "parent_id": cls.child_category.id,
            }
        )

    def test_01_root_category_complete_name(self):
        """Root category complete_name equals its own name."""
        self.assertEqual(self.root_category.complete_name, "Root Category")

    def test_02_child_category_complete_name(self):
        """Child category complete_name includes parent path separated by ' / '."""
        self.assertEqual(
            self.child_category.complete_name, "Root Category / Child Category"
        )

    def test_03_grandchild_category_complete_name(self):
        """Grandchild category complete_name includes the full hierarchy."""
        self.assertEqual(
            self.grandchild_category.complete_name,
            "Root Category / Child Category / Grandchild Category",
        )

    def test_04_content_page_complete_name(self):
        """Content page (type='content') complete_name equals its own name."""
        self.assertEqual(self.page.complete_name, "A Page")

    def test_05_display_name_uses_complete_name(self):
        """display_name is set to complete_name for all document pages."""
        self.assertEqual(
            self.child_category.display_name,
            self.child_category.complete_name,
        )
        self.assertEqual(
            self.page.display_name,
            self.page.complete_name,
        )

    def test_06_rename_parent_updates_children(self):
        """Renaming a parent category propagates to child complete_name."""
        self.root_category.name = "Renamed Root"
        self.assertEqual(
            self.child_category.complete_name, "Renamed Root / Child Category"
        )
        self.assertEqual(
            self.grandchild_category.complete_name,
            "Renamed Root / Child Category / Grandchild Category",
        )
        # restore
        self.root_category.name = "Root Category"
