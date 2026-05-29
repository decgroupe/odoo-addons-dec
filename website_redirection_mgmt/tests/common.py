# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestWebsiteRedirectionMgmtCommon(TransactionCase):
    """Common base class with shared fixtures for website_redirection_mgmt tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.WebsiteRewrite = cls.env["website.rewrite"]
        cls.WebsiteRewriteGroup = cls.env["website.rewrite.group"]
        # create a rewrite group for classification tests
        cls.group = cls.WebsiteRewriteGroup.create(
            {
                "name": "Test Campaign",
                "note": "A test campaign group",
            }
        )
        # create a basic rewrite record
        cls.rewrite = cls.WebsiteRewrite.create(
            {
                "name": "/old 🡢 /new",
                "redirect_type": "301",
                "url_from": "/old",
                "url_to": "/new",
            }
        )
