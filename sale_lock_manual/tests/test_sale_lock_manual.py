# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestSaleLockManual(TransactionCase):
    """Tests for sale_lock_manual module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "consu",
                "list_price": 10.0,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                        }
                    )
                ],
            }
        )
        cls.sale_order.action_confirm()

    def test_01_lock_confirmed_sale_order(self):
        """Lock button (action_lock) sets locked=True on a confirmed sale order."""
        self.assertEqual(self.sale_order.state, "sale")
        self.assertFalse(self.sale_order.locked)
        self.sale_order.action_lock()
        self.assertTrue(self.sale_order.locked)

    def test_02_unlock_locked_sale_order(self):
        """Unlock button (action_unlock) sets locked=False on a locked sale order."""
        self.sale_order.action_lock()
        self.assertTrue(self.sale_order.locked)
        self.sale_order.action_unlock()
        self.assertFalse(self.sale_order.locked)

    def test_03_group_manual_done_setting_exists(self):
        """The group_manual_done_setting security group is properly created."""
        group = self.env.ref(
            "sale_lock_manual.group_manual_done_setting", raise_if_not_found=False
        )
        self.assertIsNotNone(group)
        self.assertEqual(group.name, "Lock Confirmed Sales Manually")
