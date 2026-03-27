# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestPartnerSearchCity(TransactionCase):
    """Tests for partner_search_city module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()

    def test_01_search_view_fields(self):
        """Verify that the inherited search view contains the expected fields."""
        view = self.env.ref("partner_search_city.view_res_partner_search_city")
        self.assertTrue(view)
        arch = view.get_combined_arch()
        self.assertIn("zip_id", arch)
        self.assertIn("city", arch)
        self.assertIn("zip", arch)
        self.assertIn("street", arch)
