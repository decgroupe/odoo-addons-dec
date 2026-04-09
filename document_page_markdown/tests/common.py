# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestDocumentPageMarkdownCommon(TransactionCase):
    """Base class for document_page_markdown tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.page = cls.env["document.page"].create(
            {
                "name": "Test Page",
                "type": "content",
            }
        )
