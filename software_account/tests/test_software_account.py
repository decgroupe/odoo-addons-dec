# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo.tests.common import TransactionCase


class TestSoftwareAccount(TransactionCase):
    """Tests for software_account module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.supplier = cls.env["software.account.supplier"].create(
            {
                "name": "Test Supplier",
                "rules": "No sharing of credentials.",
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Software Product",
                "type": "consu",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )

    def test_01_create_supplier(self):
        """Verify that a software.account.supplier record is created correctly."""
        self.assertTrue(self.supplier.exists())
        self.assertEqual(self.supplier.name, "Test Supplier")
        self.assertEqual(self.supplier.rules, "No sharing of credentials.")

    def test_02_create_account(self):
        """Verify that a software.account record is created with all required fields."""
        account = self.env["software.account"].create(
            {
                "supplier_id": self.supplier.id,
                "login": "testuser@example.com",
                "password": "secret123",
                "email": "testuser@example.com",
                "firstname": "John",
                "lastname": "Doe",
                "question": "What is your pet's name?",
                "answer": "Buddy",
                "pin": "1234",
                "product_id": self.product.id,
                "partner_id": self.partner.id,
                "info": "Some info.",
            }
        )
        self.assertTrue(account.exists())
        self.assertEqual(account.login, "testuser@example.com")
        self.assertEqual(account.supplier_id, self.supplier)
        self.assertEqual(account.product_id, self.product)
        self.assertEqual(account.partner_id, self.partner)

    def test_03_account_form_view_fields(self):
        """Check that expected fields are present in the account form view arch."""
        view_info = self.env["software.account"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("login", field_names)
        self.assertIn("password", field_names)
        self.assertIn("email", field_names)
        self.assertIn("firstname", field_names)
        self.assertIn("lastname", field_names)
        self.assertIn("question", field_names)
        self.assertIn("answer", field_names)
        self.assertIn("pin", field_names)
        self.assertIn("product_id", field_names)
        self.assertIn("production_id", field_names)
        self.assertIn("partner_id", field_names)
        self.assertIn("datetime", field_names)
        self.assertIn("info", field_names)

    def test_04_account_list_view_fields(self):
        """Check that expected fields are present in the account list view arch."""
        view_info = self.env["software.account"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("supplier_id", field_names)
        self.assertIn("login", field_names)
        self.assertIn("email", field_names)
        self.assertIn("product_id", field_names)
        self.assertIn("partner_id", field_names)

    def test_05_supplier_form_view_fields(self):
        """Check that expected fields are present in the supplier form view arch."""
        view_info = self.env["software.account.supplier"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)
        self.assertIn("image", field_names)
        self.assertIn("rules", field_names)
        self.assertIn("account_count", field_names)

    def test_06_supplier_list_view_fields(self):
        """Check that expected fields are present in the supplier list view arch."""
        view_info = self.env["software.account.supplier"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("name", field_names)

    def test_07_account_search_view_fields(self):
        """Check that expected fields are present in the account search view arch."""
        view_info = self.env["software.account"].get_view(view_type="search")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("supplier_id", field_names)
        self.assertIn("login", field_names)
        self.assertIn("email", field_names)
        self.assertIn("product_id", field_names)
        self.assertIn("partner_id", field_names)

    def test_08_supplier_account_count(self):
        """Verify account_count reflects the number of linked accounts."""
        self.assertEqual(self.supplier.account_count, 0)
        acc1 = self.env["software.account"].create(
            {
                "supplier_id": self.supplier.id,
                "login": "user1",
                "password": "pass1",
                "email": "user1@example.com",
            }
        )
        self.supplier.invalidate_recordset()
        self.assertEqual(self.supplier.account_count, 1)
        acc2 = self.env["software.account"].create(
            {
                "supplier_id": self.supplier.id,
                "login": "user2",
                "password": "pass2",
                "email": "user2@example.com",
            }
        )
        self.supplier.invalidate_recordset()
        self.assertEqual(self.supplier.account_count, 2)
        acc1.unlink()
        acc2.unlink()

    def test_09_action_view_accounts(self):
        """Verify the smart button action returns an act_window filtered by supplier."""
        acc = self.env["software.account"].create(
            {
                "supplier_id": self.supplier.id,
                "login": "smart@example.com",
                "password": "pw",
                "email": "smart@example.com",
            }
        )
        action = self.supplier.action_view_accounts()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "software.account")
        self.assertIn(("supplier_id", "=", self.supplier.id), action["domain"])
        self.assertEqual(action["context"]["default_supplier_id"], self.supplier.id)
        acc.unlink()
