# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestSaleSummary(TransactionCase):
    """Tests for the sale_summary module."""

    @classmethod
    def setUpClass(cls):
        """Set up test data for the test class."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Customer",
                "email": "test@example.com",
                "phone": "0123456789",
            }
        )
        cls.SaleOrder = cls.env["sale.order"]

    def test_01_sale_order_summary_field_exists(self):
        """Test that the summary field is correctly added to sale.order model."""
        self.assertTrue(hasattr(self.SaleOrder, "summary"))
        field = self.SaleOrder._fields["summary"]
        self.assertEqual(field.type, "char")
        self.assertEqual(field.size, 128)

    def test_02_create_sale_order_with_summary(self):
        """Test creating a sale order with a summary."""
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": "Test order summary",
            }
        )
        self.assertEqual(order.summary, "Test order summary")

    def test_03_update_sale_order_summary(self):
        """Test updating the summary field of an existing sale order."""
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": "Initial summary",
            }
        )
        order.summary = "Updated summary"
        self.assertEqual(order.summary, "Updated summary")

    def test_04_sale_order_summary_empty(self):
        """Test creating a sale order without a summary."""
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
            }
        )
        self.assertFalse(order.summary)

    def test_05_sale_order_summary_max_length(self):
        """Test that summary field respects the 128 character limit."""
        long_summary = "A" * 256
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": long_summary,
            }
        )
        self.assertEqual(len(order.summary), 128)
        self.assertEqual(order.summary, long_summary[:128])

    def test_06_sale_order_summary_search(self):
        """Test searching sale orders by summary field."""
        order1 = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": "Premium Customer Order",
            }
        )
        order2 = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": "Standard Order",
            }
        )
        results = self.SaleOrder.search([("summary", "=", "Premium Customer Order")])
        self.assertIn(order1, results)
        self.assertNotIn(order2, results)

    def test_07_sale_order_summary_ilike_search(self):
        """Test searching sale orders by summary field using ilike operator."""
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": "VIP Customer Order",
            }
        )
        results = self.SaleOrder.search([("summary", "ilike", "VIP")])
        self.assertIn(order, results)

    def test_08_sale_order_summary_special_characters(self):
        """Test summary field with special characters."""
        special_summary = "Order #2025-001 - Client: @CompanyName (50% discount)"
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": special_summary,
            }
        )
        self.assertEqual(order.summary, special_summary)

    def test_09_sale_order_summary_unicode(self):
        """Test summary field with unicode characters."""
        unicode_summary = "Commande spéciale - Café ☕ - Français"
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": unicode_summary,
            }
        )
        self.assertEqual(order.summary, unicode_summary)

    def test_10_sale_order_summary_whitespace(self):
        """Test summary field with leading and trailing whitespace.
        Note that the web client automatically trims whitespaces.
        """
        summary_with_space = "  Order with spaces  "
        order = self.SaleOrder.create(
            {
                "partner_id": self.partner.id,
                "summary": summary_with_space,
            }
        )
        self.assertEqual(order.summary, summary_with_space)
