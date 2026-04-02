# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command
from odoo.tests.common import TransactionCase


class TestPurchaseDeliveryRate(TransactionCase):
    """Tests for purchase_delivery_rate module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test fixtures."""
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Supplier"})
        cls.product_consu = cls.env["product.product"].create(
            {
                "name": "Consumable Product",
                "type": "consu",
            }
        )
        cls.product_storable = cls.env["product.product"].create(
            {
                "name": "Storable Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.product_service = cls.env["product.product"].create(
            {
                "name": "Service Product",
                "type": "service",
            }
        )

    def _create_purchase_order(self, lines):
        """Create a purchase order with the given order lines."""
        return self.env["purchase.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create(vals) for vals in lines],
            }
        )

    def test_01_picked_rate_zero_when_nothing_received(self):
        """picked_rate is 0 when no line has been received."""
        po = self._create_purchase_order(
            [
                {
                    "product_id": self.product_consu.id,
                    "product_qty": 10.0,
                    "price_unit": 5.0,
                },
            ]
        )
        self.assertEqual(po.picked_rate, 0.0)

    def test_02_picked_rate_100_when_all_received(self):
        """picked_rate is 100 when all non-service lines are fully received."""
        po = self._create_purchase_order(
            [
                {
                    "product_id": self.product_consu.id,
                    "product_qty": 5.0,
                    "price_unit": 10.0,
                },
                {
                    "product_id": self.product_storable.id,
                    "product_qty": 3.0,
                    "price_unit": 20.0,
                },
            ]
        )
        # simulate full receipt by directly writing qty_received
        po.order_line[0].qty_received = 5.0
        po.order_line[1].qty_received = 3.0
        po._compute_picked_rate()
        self.assertEqual(po.picked_rate, 100.0)

    def test_03_picked_rate_partial(self):
        """picked_rate is 50 when half the eligible lines are fully received."""
        po = self._create_purchase_order(
            [
                {
                    "product_id": self.product_consu.id,
                    "product_qty": 4.0,
                    "price_unit": 10.0,
                },
                {
                    "product_id": self.product_storable.id,
                    "product_qty": 4.0,
                    "price_unit": 10.0,
                },
            ]
        )
        # only first line is fully received
        po.order_line[0].qty_received = 4.0
        po.order_line[1].qty_received = 0.0
        po._compute_picked_rate()
        self.assertEqual(po.picked_rate, 50.0)

    def test_04_service_lines_excluded(self):
        """Service lines are excluded from the picked_rate computation."""
        po = self._create_purchase_order(
            [
                {
                    "product_id": self.product_service.id,
                    "product_qty": 1.0,
                    "price_unit": 100.0,
                },
            ]
        )
        po._compute_picked_rate()
        self.assertEqual(po.picked_rate, 0.0)

    def test_05_action_update_picked_rate(self):
        """action_update_picked_rate triggers recomputation of picked_rate."""
        po = self._create_purchase_order(
            [
                {
                    "product_id": self.product_consu.id,
                    "product_qty": 6.0,
                    "price_unit": 5.0,
                },
            ]
        )
        po.order_line[0].qty_received = 6.0
        po.action_update_picked_rate()
        self.assertEqual(po.picked_rate, 100.0)

    def test_06_list_view_fields(self):
        """picked_rate field is present in the combined list view arch."""
        view_info = self.env["purchase.order"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("picked_rate", field_names)

    def test_07_form_view_fields(self):
        """picked_rate field is present in the combined form view arch."""
        view_info = self.env["purchase.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("picked_rate", field_names)
