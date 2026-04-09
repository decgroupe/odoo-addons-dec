# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from .common import TestDocumentPageMarkdownCommon


class TestDocumentPageMarkdown(TestDocumentPageMarkdownCommon):
    """Tests for document_page_markdown module."""

    def test_01_content_markdown_field_default(self):
        """Check that content_markdown is empty by default on a new page."""
        self.assertFalse(self.page.content_markdown)

    def test_02_write_creates_history_on_markdown_change(self):
        """Check that writing content_markdown creates a new history entry."""
        initial_history_count = len(self.page.history_ids)
        self.page.write({"content_markdown": "# Hello World"})
        self.assertEqual(len(self.page.history_ids), initial_history_count + 1)
        self.assertEqual(self.page.history_head.content_markdown, "# Hello World")

    def test_03_write_no_history_when_markdown_unchanged(self):
        """Check that writing the same markdown does not create extra history."""
        self.page.write({"content_markdown": "# Same Content"})
        count_after_first = len(self.page.history_ids)
        self.page.write({"content_markdown": "# Same Content"})
        self.assertEqual(len(self.page.history_ids), count_after_first)

    def test_04_create_history_adds_markdown_when_missing(self):
        """Check that _create_history injects markdown content when not provided."""
        self.page.write({"content_markdown": "# My Markdown"})
        # call _create_history without content_markdown key
        self.page._create_history(
            {
                "page_id": self.page.id,
                "name": "v2",
                "content": "<p>html</p>",
            }
        )
        last_history = self.page.history_ids[0]
        self.assertEqual(last_history.content_markdown, "# My Markdown")

    def test_05_create_history_keeps_provided_markdown(self):
        """Check that _create_history keeps provided markdown content as-is."""
        self.page._create_history(
            {
                "page_id": self.page.id,
                "name": "v3",
                "content": "<p>html</p>",
                "content_markdown": "# Provided Markdown",
            }
        )
        last_history = self.page.history_ids[0]
        self.assertEqual(last_history.content_markdown, "# Provided Markdown")

    def test_06_write_skips_history_for_category_pages(self):
        """Check that category-type pages do not trigger history creation."""
        category = self.env["document.page"].create(
            {
                "name": "Test Category",
                "type": "category",
            }
        )
        initial_history_count = len(category.history_ids)
        category.write({"content_markdown": "# Category Markdown"})
        self.assertEqual(len(category.history_ids), initial_history_count)

    def test_07_form_view_fields(self):
        """Check that content_markdown field is present in combined form view."""
        view_info = self.env["document.page"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("content_markdown", field_names)

    def test_08_history_form_view_fields(self):
        """Check that content_markdown is present in the history form view."""
        view_info = self.env["document.page.history"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("content_markdown", field_names)
