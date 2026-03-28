# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from lxml import etree

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestDocumentPageDefault(TransactionCase):
    """Tests for document_page_default module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.page = cls.env["document.page"].create({"name": "Test Page"})

    def test_01_format_name(self):
        """Test that _format_name returns the correct formatted revision string."""
        self.assertEqual(self.page._format_name(1), "Rev 01")
        self.assertEqual(self.page._format_name(5), "Rev 05")
        self.assertEqual(self.page._format_name(42), "Rev 42")

    def test_02_view_draft_fields_not_required(self):
        """Verify our view override makes draft_name and draft_summary not required."""
        view_id = self.env.ref("document_page_default.view_wiki_form_view").id
        view_data = self.env["document.page"].get_view(
            view_id=view_id,
            view_type="form",
        )
        arch = etree.fromstring(view_data["arch"])
        for fname in ("draft_name", "draft_summary"):
            nodes = arch.xpath(f"//field[@name='{fname}']")
            self.assertTrue(nodes, msg=f"field '{fname}' not found in view")
            required = nodes[0].get("required", "")
            self.assertNotEqual(
                required,
                "True",
                msg=f"'{fname}' should not be required in our view override",
            )

    def test_03_history_naming(self):
        """Test that _create_history names each revision sequentially as 'Rev NN'."""
        page = self.env["document.page"].create({"name": "Test Page for History"})
        # trigger first history entry by writing content
        page.write({"content": "<p>First content</p>"})
        self.assertEqual(len(page.history_ids), 1)
        self.assertEqual(page.history_ids[0].name, "Rev 01")
        # trigger second history entry by changing content
        page.write({"content": "<p>Second content</p>"})
        self.assertEqual(len(page.history_ids), 2)
        self.assertEqual(page.history_ids[0].name, "Rev 02")

    def test_04_history_naming_via_form(self):
        """Test sequential revision naming using the Form helper."""
        view = "document_page.view_wiki_form"
        category = self.env["document.page"].create(
            {"name": "Test Category", "type": "category"}
        )
        with Form(
            self.env["document.page"],
            view=view,
        ) as form:
            form.name = "Test Page for History (Form)"
            form.parent_id = category
            form.content = "<p>First content</p>"
        page = self.env["document.page"].search(
            [("name", "=", "Test Page for History (Form)")], limit=1
        )
        self.assertEqual(len(page.history_ids), 1)
        self.assertEqual(page.history_ids[0].name, "Rev 01")
        # edit content a second time to trigger a second history entry
        with Form(page, view=view) as form:
            form.content = "<p>Second content</p>"
        self.assertEqual(len(page.history_ids), 2)
        self.assertEqual(page.history_ids[0].name, "Rev 02")
