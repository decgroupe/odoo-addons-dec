# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductServiceNoRoutes(TransactionCase):
    def _create_confirm_assign_stock_move(self, product, quantity=1):
        move_in = self.env["stock.move"].create(
            {
                "name": "test_customer",
                "location_id": self.customer_location.id,
                "location_dest_id": self.stock_location.id,
                "product_id": product.id,
                "product_uom": self.uom_unit.id,
                "product_uom_qty": quantity,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        move_in._action_confirm()
        move_in._action_assign()
        return move_in

    def setUp(self):
        super().setUp()
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        # References to locations
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        # Consumable Product (type='consu')
        self.consumable_product = self.env["product.product"].create(
            {
                "name": "My Consumable Product",
                "type": "consu",
                "is_storable": False,
                "standard_price": 10.0,
                "list_price": 15.0,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "route_ids": [],
            }
        )
        # Storable Product (was type='product' in previous Odoo versions)
        self.storable_product = self.env["product.product"].create(
            {
                "name": "My Storable Product",
                "type": "consu",
                "is_storable": True,
                "standard_price": 20.0,
                "list_price": 30.0,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "route_ids": [],
            }
        )
        # Create a fake route since buy or manufacture routes are not available here
        self.fake_route = self.env["stock.route"].create(
            {
                "name": "Fake route -> none",
                "product_selectable": True,
            }
        )

    def test_02_change_consumable_to_service(self):
        def _internal_test(product):
            self.assertFalse(product.route_ids)
            product.route_ids += self.fake_route
            self.assertTrue(self.consumable_product.route_ids)
            product.type = "service"
            self.assertFalse(product.route_ids)

        _internal_test(self.consumable_product)
        _internal_test(self.consumable_product.product_variant_id)

    def test_03_change_stockable_to_service(self):
        def _internal_test(product):
            self.assertFalse(product.route_ids)
            product.route_ids += self.fake_route
            self.assertTrue(product.route_ids)
            product.type = "service"
            self.assertFalse(product.route_ids)

        _internal_test(self.storable_product)
        # unset existing fake route previously added
        self.storable_product.route_ids = False
        _internal_test(self.storable_product.product_variant_id)

    def test_04_change_stockable_already_used_to_service(self):
        def _internal_test(product):
            self.assertFalse(product.route_ids)
            # https://github.com/odoo/odoo/pull/239284
            # [FIX] stock: Ensure that "is_storable" is properly computed
            with (
                self.assertRaisesRegex(
                    UserError,
                    "You can not change the inventory tracking of a product.*",
                ),
                self.cr.savepoint(),
            ):
                product.route_ids += self.fake_route
                self.assertTrue(product.route_ids)
                product.type = "service"

        self._create_confirm_assign_stock_move(self.storable_product, quantity=5)
        _internal_test(self.storable_product)
        _internal_test(self.storable_product.product_variant_id)

    def test_05_create_service_with_route(self):
        myservice = self.env["product.product"].create(
            {
                "name": "My Super Service",
                "type": "service",
                "route_ids": [(4, self.fake_route.id)],
            }
        )
        self.assertFalse(myservice.route_ids)
