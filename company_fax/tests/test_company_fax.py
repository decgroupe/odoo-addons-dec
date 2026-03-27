# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestCompanyFax(TransactionCase):
    """Tests for company_fax module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.company = cls.env.company

    def test_01_fax_field_exists_on_company(self):
        """Verify the fax field is available on res.company."""
        self.assertIn("fax", self.env["res.company"]._fields)

    def test_02_fax_write_on_company_propagates_to_partner(self):
        """Writing fax on company updates the related partner fax."""
        self.company.fax = "+33123456789"
        self.assertEqual(self.company.partner_id.fax, "+33123456789")

    def test_03_fax_write_on_partner_propagates_to_company(self):
        """Writing fax on partner is reflected on company via related field."""
        self.company.partner_id.fax = "+33987654321"
        self.company.invalidate_recordset()
        self.assertEqual(self.company.fax, "+33987654321")

    def test_04_fax_stores_value(self):
        """The fax field is stored on company."""
        field = self.env["res.company"]._fields["fax"]
        self.assertTrue(field.store)
        self.assertFalse(field.readonly)
