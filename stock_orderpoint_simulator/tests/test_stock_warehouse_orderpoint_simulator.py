# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by GitHub Copilot <copilot at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestStockWarehouseOrderpointSimulator(TransactionCase):
    """Test cases for stock warehouse orderpoint simulator wizard"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Company = cls.env["res.company"]
        cls.Product = cls.env["product.product"]
        cls.Category = cls.env["product.category"]
        cls.Warehouse = cls.env["stock.warehouse"]
        cls.Orderpoint = cls.env["stock.warehouse.orderpoint"]
        cls.Simulator = cls.env["stock.warehouse.orderpoint.simulator"]
        cls.Location = cls.env["stock.location"]
        cls.Quant = cls.env["stock.quant"]
        cls.UOM = cls.env["uom.uom"]

        cls.company = cls.Company.create({"name": "Test Company"})

        # Get or create warehouse
        cls.warehouse = cls.Warehouse.search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        if not cls.warehouse:
            cls.warehouse = cls.Warehouse.create(
                {
                    "name": "Test Warehouse",
                    "company_id": cls.company.id,
                }
            )

        cls.stock_location = cls.Location.search(
            [
                ("usage", "=", "internal"),
                ("warehouse_id", "=", cls.warehouse.id),
            ],
            limit=1,
        )
        # Create test product
        cls.product = cls.Product.create(
            {
                "name": "Test Product",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.Category.search([], limit=1).id,
                "uom_id": cls.UOM.search(
                    [("category_id.name", "=", "Unit")], limit=1
                ).id,
                "uom_po_id": cls.UOM.search(
                    [("category_id.name", "=", "Unit")], limit=1
                ).id,
            }
        )
        # Create orderpoint
        cls.orderpoint = cls.Orderpoint.create(
            {
                "company_id": cls.company.id,
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.stock_location.id,
                "product_id": cls.product.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
            }
        )

    def test_01_default_get_with_orderpoint(self):
        """Test default_get initializes from active orderpoint"""
        context = {
            "active_id": self.orderpoint.id,
            "active_model": "stock.warehouse.orderpoint",
        }
        result = self.Simulator.with_context(**context).default_get(
            [
                "origin_orderpoint_id",
                "product_min_qty",
                "product_max_qty",
                "product_uom_po_id",
            ]
        )
        self.assertEqual(result["origin_orderpoint_id"], self.orderpoint.id)
        self.assertEqual(result["product_min_qty"], 10.0)
        self.assertEqual(result["product_max_qty"], 50.0)
        self.assertEqual(result["product_uom_po_id"], self.product.uom_po_id.id)

    def test_02_default_get_without_active_id(self):
        """Test default_get with no active_id returns empty dict"""
        context = {
            "active_id": None,
            "active_model": "stock.warehouse.orderpoint",
        }
        result = self.Simulator.with_context(**context).default_get(
            ["origin_orderpoint_id", "product_min_qty"]
        )
        self.assertNotIn("origin_orderpoint_id", result)

    def test_03_default_get_wrong_model(self):
        """Test default_get with wrong active_model doesn't populate values"""
        context = {
            "active_id": self.orderpoint.id,
            "active_model": "res.partner",
        }
        result = self.Simulator.with_context(**context).default_get(
            ["origin_orderpoint_id"]
        )
        self.assertNotIn("origin_orderpoint_id", result)

    def test_04_onchange_quantity_below_min(self):
        """Test quantity calculation when available qty is below minimum"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 5.0,
                "qty_multiple": 1.0,
            }
        )
        # needed_qty = max(10, 50) - 5 = 45
        self.assertEqual(simulator.needed_qty, 45.0)
        # remaining_qty = 45 % 1 = 0
        self.assertEqual(simulator.remaining_qty, 0.0)
        # available_qty < min_qty, so qty_to_order = needed_qty = 45
        self.assertEqual(simulator.qty_to_order, 45.0)

    def test_05_onchange_quantity_above_min(self):
        """Test quantity calculation when available qty is above minimum"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 20.0,
                "qty_multiple": 1.0,
            }
        )
        # available_qty >= min_qty, so qty_to_order should be 0
        self.assertEqual(simulator.qty_to_order, 0.0)

    def test_06_onchange_quantity_with_multiple(self):
        """Test quantity calculation with qty_multiple > 1"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 5.0,
                "qty_multiple": 10.0,
            }
        )
        # needed_qty = max(10, 50) - 5 = 45
        self.assertEqual(simulator.needed_qty, 45.0)
        # remaining_qty = 45 % 10 = 5
        self.assertEqual(simulator.remaining_qty, 5.0)
        # available_qty < min_qty and remaining_qty > 0
        # qty_to_order = 45 + 10 - 5 = 50
        self.assertEqual(simulator.qty_to_order, 50.0)

    def test_07_onchange_quantity_no_remainder(self):
        """Test quantity calculation when needed_qty is exact multiple"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 5.0,
                "qty_multiple": 5.0,
            }
        )
        # needed_qty = 45, qty_multiple = 5
        # remaining_qty = 45 % 5 = 0
        self.assertEqual(simulator.remaining_qty, 0.0)
        # available_qty < min_qty and remaining_qty = 0
        # qty_to_order = needed_qty = 45
        self.assertEqual(simulator.qty_to_order, 45.0)

    def test_08_onchange_quantity_zero_multiple(self):
        """Test quantity calculation with qty_multiple = 0"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 5.0,
                "qty_multiple": 0.0,
            }
        )
        # remaining_qty should be 0 when qty_multiple is 0
        self.assertEqual(simulator.remaining_qty, 0.0)

    def test_09_action_apply_updates_orderpoint(self):
        """Test action_apply updates the origin orderpoint"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 15.0,
                "product_max_qty": 60.0,
                "available_qty": 5.0,
                "qty_multiple": 1.0,
            }
        )
        simulator.action_apply()
        self.assertEqual(self.orderpoint.product_min_qty, 15.0)
        self.assertEqual(self.orderpoint.product_max_qty, 60.0)

    def test_10_onchange_quantity_edge_case_same_min_max(self):
        """Test quantity calculation when min and max are the same"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 50.0,
                "product_max_qty": 50.0,
                "available_qty": 5.0,
                "qty_multiple": 1.0,
            }
        )
        # needed_qty = max(50, 50) - 5 = 45
        self.assertEqual(simulator.needed_qty, 45.0)
        self.assertEqual(simulator.qty_to_order, 45.0)

    def test_11_onchange_quantity_available_equals_max(self):
        """Test quantity calculation when available equals max"""
        simulator = self.Simulator.create(
            {
                "origin_orderpoint_id": self.orderpoint.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "available_qty": 50.0,
                "qty_multiple": 1.0,
            }
        )
        # needed_qty = 50 - 50 = 0
        self.assertEqual(simulator.needed_qty, 0.0)
        # available_qty >= min_qty, so qty_to_order = 0
        self.assertEqual(simulator.qty_to_order, 0.0)
