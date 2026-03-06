# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestMrpConsumeLine(TransactionCase):
    """Tests for MrpConsumeLine wizard model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrp_consume_line_model = cls.env["mrp.consume.line"]
        cls.mail_activity_model = cls.env["mail.activity"]
        cls.product_model = cls.env["product.product"]
        cls.product_template_model = cls.env["product.template"]
        cls.product = cls.product_model.create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
            }
        )

    def test_01_compute_product_location_with_all_fields(self):
        """Test _compute_product_location with rack, row, and case values."""
        self.product.loc_rack = "A"
        self.product.loc_row = "1"
        self.product.loc_case = "B1"
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": self.product.id,
            }
        )
        # WARNING: separator is a non-breaking space (U+00A0) and not a regular space.
        self.assertEqual(consume_line.product_location, "A . 1 . B1")

    def test_02_compute_product_location_with_partial_fields(self):
        """Test _compute_product_location with only rack and row."""
        product = self.product_model.create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
                "loc_rack": "C",
                "loc_row": "2",
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        # WARNING: separator is a non-breaking space (U+00A0) and not a regular space.
        self.assertEqual(consume_line.product_location, "C . 2")

    def test_03_compute_product_location_with_single_field(self):
        """Test _compute_product_location with only rack."""
        product = self.product_model.create(
            {
                "name": "Test Product 3",
                "type": "consu",
                "is_storable": True,
                "loc_rack": "D",
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        # WARNING: separator is a non-breaking space (U+00A0) and not a regular space.
        self.assertEqual(consume_line.product_location, "D")

    def test_04_compute_product_location_without_fields(self):
        """Test _compute_product_location with no location fields."""
        product = self.product_model.create(
            {
                "name": "Test Product 4",
                "type": "consu",
                "is_storable": True,
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        # WARNING: separator is a non-breaking space (U+00A0) and not a regular space.
        self.assertEqual(consume_line.product_location, "")

    def test_05_action_create_inventory_activity_with_todo_activity(self):
        """Test creating inventory activity with mail.activity.data.todo."""
        product = self.product_model.create(
            {
                "name": "Test Product 5",
                "type": "consu",
                "is_storable": True,
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        consume_line.action_create_inventory_activity()
        self.assertTrue(consume_line.inventory_activity_id)
        self.assertEqual(
            consume_line.inventory_activity_id.res_id, product.product_tmpl_id.id
        )
        self.assertEqual(
            consume_line.inventory_activity_id.res_model_id,
            self.env.ref("product.model_product_template"),
        )

    def test_06_action_create_inventory_activity_summary(self):
        """Test that inventory activity summary is correctly set."""
        product = self.product_model.create(
            {
                "name": "Test Product 6",
                "type": "consu",
                "is_storable": True,
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        consume_line.action_create_inventory_activity()
        expected_summary = self.env._("Requires inventory")
        self.assertEqual(consume_line.inventory_activity_id.summary, expected_summary)

    def test_09_ensure_one_in_action_create_inventory_activity(self):
        """Test that action_create_inventory_activity respects ensure_one."""
        product = self.product_model.create(
            {
                "name": "Test Product 9",
                "type": "consu",
                "is_storable": True,
            }
        )
        consume_line_1 = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        consume_line_2 = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        combined = consume_line_1 | consume_line_2
        with self.assertRaises(ValueError):
            combined.action_create_inventory_activity()

    def test_10_product_location_update_on_field_change(self):
        """Test that product_location updates when location fields change."""
        product = self.product_model.create(
            {
                "name": "Test Product 10",
                "type": "consu",
                "is_storable": True,
                "loc_rack": "A",
            }
        )
        consume_line = self.mrp_consume_line_model.create(
            {
                "product_id": product.id,
            }
        )
        # WARNING: separator is a non-breaking space (U+00A0) and not a regular space.
        self.assertEqual(consume_line.product_location, "A")
        product.loc_row = "1"
        consume_line.invalidate_recordset()
        self.assertEqual(consume_line.product_location, "A . 1")
        product.loc_case = "B1"
        consume_line.invalidate_recordset()
        self.assertEqual(consume_line.product_location, "A . 1 . B1")
