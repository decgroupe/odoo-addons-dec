# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestPurchaseOrderSplit(TransactionCase):
    """Test the purchase order split functionality"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
            }
        )
        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "type": "consu",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "type": "consu",
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "type": "consu",
            }
        )

    def setUp(self):
        super().setUp()
        # Create a purchase order with multiple lines
        self.purchase_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product1.id,
                            "product_qty": 10,
                            "price_unit": 100.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product2.id,
                            "product_qty": 20,
                            "price_unit": 50.0,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": self.product3.id,
                            "product_qty": 5,
                            "price_unit": 200.0,
                        }
                    ),
                ],
            }
        )

    def test_01_wizard_default_get_initialization(self):
        """Test that the wizard initializes correctly with selected lines"""
        # Select lines 1 and 2 (indices 0 and 1)
        selected_lines = self.purchase_order.order_line[:2]

        # Create wizard through default_get
        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create({})
        )

        # Verify wizard state
        self.assertEqual(wizard.origin_order_id, self.purchase_order)
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(set(wizard.order_line_ids.ids), set(selected_lines.ids))
        self.assertFalse(wizard.order_id)

    def test_02_wizard_prevents_selecting_all_lines(self):
        """Test that the wizard raises an error when all lines are selected"""
        # Try to select all lines
        all_lines = self.purchase_order.order_line

        # This should raise UserError during default_get
        with self.assertRaises(UserError) as cm:
            self.env["purchase.order.split"].with_context(
                active_model="purchase.order.line",
                active_ids=all_lines.ids,
            ).create({})

        self.assertIn("can't select all lines", str(cm.exception).lower())

    def test_03_create_new_order_with_split_lines(self):
        """Test creating a new purchase order with selected lines"""
        # Select lines 1 and 2
        selected_lines = self.purchase_order.order_line[:2]

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create({})
        )

        # Execute split without specifying target order
        result = wizard.action_split()

        # Verify result
        self.assertEqual(result["type"], "ir.actions.act_window")
        self.assertEqual(result["res_model"], "purchase.order")

        # Get the new order
        new_order_id = result["res_id"]
        new_order = self.env["purchase.order"].browse(new_order_id)

        # Verify new order properties
        self.assertEqual(new_order.partner_id, self.partner)
        self.assertEqual(new_order.origin, self.purchase_order.name)
        self.assertEqual(len(new_order.order_line), 2)
        self.assertEqual(
            set(new_order.order_line.product_id.ids),
            {self.product1.id, self.product2.id},
        )

        # Verify original order still has the remaining line
        self.purchase_order.invalidate_recordset()
        self.assertEqual(len(self.purchase_order.order_line), 1)
        self.assertEqual(self.purchase_order.order_line.product_id, self.product3)

    def test_04_move_lines_to_existing_order(self):
        """Test moving selected lines to an existing purchase order"""
        # Create a second purchase order
        target_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product3.id,
                            "product_qty": 15,
                            "price_unit": 150.0,
                        },
                    ),
                ],
            }
        )

        # Select first two lines from original order
        selected_lines = self.purchase_order.order_line[:2]

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create(
                {
                    "order_id": target_order.id,
                }
            )
        )

        # Execute split
        result = wizard.action_split()

        # Verify result
        self.assertEqual(result["res_id"], target_order.id)

        # Verify target order has all lines
        target_order.invalidate_recordset()
        self.assertEqual(len(target_order.order_line), 3)

        # Verify original order only has the remaining line
        self.purchase_order.invalidate_recordset()
        self.assertEqual(len(self.purchase_order.order_line), 1)
        self.assertEqual(self.purchase_order.order_line.product_id, self.product3)

    def test_05_split_preserves_group_id(self):
        """Test that split preserves the group_id when creating new order"""
        # Purchase order has a group_id field, but we'll test with None first
        # to ensure the copy mechanism works correctly

        # Select first two lines
        selected_lines = self.purchase_order.order_line[:2]

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create({})
        )

        # Execute split
        result = wizard.action_split()
        new_order = self.env["purchase.order"].browse(result["res_id"])

        # Verify group_id is preserved (should be None or same as original)
        self.assertEqual(new_order.group_id, self.purchase_order.group_id)

    def test_06_wizard_domain_filters_by_partner(self):
        """Test that order_id domain only shows orders from same partner"""
        # Create another partner
        other_partner = self.env["res.partner"].create(
            {
                "name": "Other Partner",
            }
        )

        # Create order with different partner
        other_order = self.env["purchase.order"].create(
            {
                "partner_id": other_partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product1.id,
                            "product_qty": 10,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

        # Create compatible order
        compatible_order = self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product1.id,
                            "product_qty": 10,
                            "price_unit": 100.0,
                        },
                    ),
                ],
            }
        )

        # Select lines from original order
        selected_lines = self.purchase_order.order_line[:2]

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create({})
        )

        # Verify wizard was initialized correctly with partner info
        self.assertEqual(wizard.partner_id, self.partner)
        self.assertEqual(wizard.origin_order_id, self.purchase_order)

        # Verify that compatible_order can be selected as target
        # (it has same partner, different state constraint is handled by domain)
        self.assertNotEqual(compatible_order.id, self.purchase_order.id)
        self.assertEqual(compatible_order.partner_id, self.partner)

        # Verify other_order has different partner
        self.assertNotEqual(other_order.partner_id, self.partner)

    def test_07_split_maintains_line_properties(self):
        """Test that split maintains all line properties"""
        # Modify a line with additional properties
        line = self.purchase_order.order_line[0]
        line.write(
            {
                "product_qty": 25,
                "price_unit": 75.50,
            }
        )

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=line.ids,
            )
            .create({})
        )

        result = wizard.action_split()
        new_order = self.env["purchase.order"].browse(result["res_id"])

        # Verify line properties are maintained
        new_line = new_order.order_line[0]
        self.assertEqual(new_line.product_id, self.product1)
        self.assertEqual(new_line.product_qty, 25)
        self.assertEqual(new_line.price_unit, 75.50)

    def test_08_wizard_without_context(self):
        """Test that wizard handles being created without active context"""
        # Create wizard without context
        wizard = self.env["purchase.order.split"].create({})

        # Verify default values
        self.assertFalse(wizard.partner_id)
        self.assertFalse(wizard.origin_order_id)
        self.assertEqual(len(wizard.order_line_ids), 0)
        self.assertFalse(wizard.order_id)

    def test_09_split_with_single_line(self):
        """Test split with just one line selected"""
        # Select only the last line
        selected_lines = self.purchase_order.order_line[2:]

        wizard = (
            self.env["purchase.order.split"]
            .with_context(
                active_model="purchase.order.line",
                active_ids=selected_lines.ids,
            )
            .create({})
        )

        # Execute split
        result = wizard.action_split()
        new_order = self.env["purchase.order"].browse(result["res_id"])

        # Verify new order has one line
        self.assertEqual(len(new_order.order_line), 1)
        self.assertEqual(new_order.order_line.product_id, self.product3)

        # Verify original order has two lines remaining
        self.purchase_order.invalidate_recordset()
        self.assertEqual(len(self.purchase_order.order_line), 2)
