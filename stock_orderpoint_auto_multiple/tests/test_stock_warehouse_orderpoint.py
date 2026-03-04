# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.tests.common import TransactionCase


class TestStockWarehouseOrderpoint(TransactionCase):
    """test stock warehouse orderpoint auto multiple functionality"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # create product category
        cls.product_category = cls.env["product.category"].create(
            {
                "name": "Test Category",
            }
        )
        # create UoM category for units
        cls.uom_categ_unit = cls.env["uom.category"].create(
            {
                "name": "Test Unit Category",
            }
        )
        # create base UoM (Unit)
        cls.uom_unit = cls.env["uom.uom"].create(
            {
                "name": "Unit(s)",
                "category_id": cls.uom_categ_unit.id,
                "factor": 1.0,
                "uom_type": "reference",
                "rounding": 0.01,
            }
        )
        # create UoM with factor_inv = 12 (dozen)
        cls.uom_dozen = cls.env["uom.uom"].create(
            {
                "name": "Dozen(s)",
                "category_id": cls.uom_categ_unit.id,
                "factor": 1.0 / 12.0,
                "uom_type": "bigger",
                "rounding": 0.01,
            }
        )
        # create UoM with factor_inv = 100 (hundred)
        cls.uom_hundred = cls.env["uom.uom"].create(
            {
                "name": "Hundred(s)",
                "category_id": cls.uom_categ_unit.id,
                "factor": 1.0 / 100.0,
                "uom_type": "bigger",
                "rounding": 0.01,
            }
        )
        # create product with default purchase UoM
        cls.product_a = cls.env["product.product"].create(
            {
                "name": "Product A",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.product_category.id,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_dozen.id,
            }
        )
        # create product with different purchase UoM
        cls.product_b = cls.env["product.product"].create(
            {
                "name": "Product B",
                "type": "consu",
                "is_storable": True,
                "categ_id": cls.product_category.id,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_hundred.id,
            }
        )
        # create warehouse
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        if not cls.warehouse:
            cls.warehouse = cls.env["stock.warehouse"].create(
                {
                    "name": "Test Warehouse",
                    "code": "TEST",
                }
            )

    def test_01_qty_multiple_computation_on_create(self):
        """test that qty_multiple is computed when creating orderpoint"""
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product_a.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
            }
        )
        # check that qty_multiple equals product's purchase UoM factor_inv
        self.assertEqual(
            orderpoint.qty_multiple,
            self.product_a.uom_po_id.factor_inv,
            "qty_multiple should equal product purchase UoM factor_inv",
        )
        self.assertEqual(
            orderpoint.qty_multiple,
            12.0,
            "qty_multiple should be 12.0 for dozen UoM",
        )

    def test_02_qty_multiple_recomputation_on_product_change(self):
        """test that qty_multiple is recomputed when product changes"""
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product_a.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
            }
        )
        # verify initial value
        self.assertEqual(
            orderpoint.qty_multiple,
            12.0,
            "initial qty_multiple should be 12.0",
        )
        # change product to product_b with different purchase UoM
        orderpoint.product_id = self.product_b
        # check that qty_multiple is recomputed
        self.assertEqual(
            orderpoint.qty_multiple,
            self.product_b.uom_po_id.factor_inv,
            "qty_multiple should update when product changes",
        )
        self.assertEqual(
            orderpoint.qty_multiple,
            100.0,
            "qty_multiple should be 100.0 for hundred UoM",
        )

    def test_03_qty_multiple_recomputation_on_uom_change(self):
        """test that qty_multiple is recomputed when product UoM changes"""
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product_a.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
            }
        )
        # verify initial value
        self.assertEqual(
            orderpoint.qty_multiple,
            12.0,
            "initial qty_multiple should be 12.0",
        )
        # change product's purchase UoM
        self.product_a.uom_po_id = self.uom_hundred
        # check that qty_multiple is recomputed
        self.assertEqual(
            orderpoint.qty_multiple,
            100.0,
            "qty_multiple should update when product purchase UoM changes",
        )

    def test_04_qty_multiple_with_unit_uom(self):
        """test qty_multiple when purchase UoM is the reference unit"""
        product_c = self.env["product.product"].create(
            {
                "name": "Product C",
                "type": "consu",
                "is_storable": True,
                "categ_id": self.product_category.id,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
            }
        )
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": product_c.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 5.0,
                "product_max_qty": 20.0,
            }
        )
        # check that qty_multiple is 1.0 for reference unit
        self.assertEqual(
            orderpoint.qty_multiple,
            1.0,
            "qty_multiple should be 1.0 for reference UoM",
        )

    def test_05_qty_multiple_field_is_stored(self):
        """test that qty_multiple field is stored in database"""
        orderpoint = self.env["stock.warehouse.orderpoint"].create(
            {
                "product_id": self.product_a.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
            }
        )
        # invalidate cache to force read from database
        orderpoint.invalidate_recordset()
        # value should still be available (proving it's stored)
        self.assertEqual(
            orderpoint.qty_multiple,
            12.0,
            "qty_multiple should be stored and retrievable from database",
        )
