# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestResUsersVcard(TransactionCase):
    """Tests for res_users_vcard module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.company.write({"name": "Test Company"})
        cls.address = cls.env["res.partner"].create(
            {
                "name": "Test Address",
                "street": "123 Main St",
                "street2": "Suite 4",
                "city": "Paris",
                "zip": "75001",
                "country_id": cls.env.ref("base.fr").id,
                "phone": "+33 1 23 45 67 89",
                "website": "https://example.com",
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "John Doe",
                "work_email": "john.doe@test.com",
                "mobile_phone": "+33 6 12 34 56 78",
                "job_title": "Software Engineer",
                "company_id": cls.company.id,
                "address_id": cls.address.id,
            }
        )

    def test_01_vcard_contains_required_markers(self):
        """VCard output starts with BEGIN:VCARD and ends with END:VCARD."""
        vcard = self.employee._generate_vcard()
        self.assertTrue(vcard.startswith("BEGIN:VCARD"))
        self.assertTrue(vcard.strip().endswith("END:VCARD"))

    def test_02_vcard_version(self):
        """VCard output declares version 2.1."""
        vcard = self.employee._generate_vcard()
        self.assertIn("VERSION:2.1", vcard)

    def test_03_vcard_contains_employee_name(self):
        """VCard output contains the employee full name."""
        vcard = self.employee._generate_vcard()
        self.assertIn("FN:John Doe", vcard)

    def test_04_vcard_contains_company(self):
        """VCard output contains the company name."""
        vcard = self.employee._generate_vcard()
        self.assertIn("ORG:Test Company", vcard)

    def test_05_vcard_contains_job_title(self):
        """VCard output contains the job title."""
        vcard = self.employee._generate_vcard()
        self.assertIn("TITLE:Software Engineer", vcard)

    def test_06_vcard_contains_email(self):
        """VCard output contains the work email."""
        vcard = self.employee._generate_vcard()
        self.assertIn("EMAIL;TYPE=INTERNET,pref:john.doe@test.com", vcard)

    def test_07_vcard_contains_mobile(self):
        """VCard output contains the mobile phone number."""
        vcard = self.employee._generate_vcard()
        self.assertIn("TEL;TYPE=CELL:", vcard)

    def test_08_vcard_contains_work_phone(self):
        """VCard output contains the work phone number from address."""
        vcard = self.employee._generate_vcard()
        self.assertIn("TEL;TYPE=WORK:", vcard)

    def test_09_vcard_contains_address(self):
        """VCard output contains the address fields."""
        vcard = self.employee._generate_vcard()
        self.assertIn("ADR;TYPE=WORK:", vcard)
        self.assertIn("123 Main St", vcard)
        self.assertIn("Paris", vcard)

    def test_10_vcard_contains_url(self):
        """VCard output contains the website URL from address."""
        vcard = self.employee._generate_vcard()
        self.assertIn("URL:https://example.com", vcard)

    def test_11_vcard_no_fax_field(self):
        """VCard output does not include a FAX field (removed in 18.0)."""
        vcard = self.employee._generate_vcard()
        self.assertNotIn("TYPE=FAX", vcard)
