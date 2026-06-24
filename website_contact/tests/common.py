# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestWebsiteContactCommon(TransactionCase):
    """Base class with shared fixtures for website_contact tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.HelpdeskCategory = cls.env["helpdesk.ticket.category"]
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.CrmLead = cls.env["crm.lead"]
        cls.category = cls.HelpdeskCategory.create(
            {
                "name": "Test Category",
                "sequence": 10,
                "public_filter": "test_filter",
            }
        )
