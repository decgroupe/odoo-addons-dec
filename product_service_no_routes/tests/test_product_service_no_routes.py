# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2023

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestProductServiceNoRoutes(TransactionCase):
    def setUp(self):
        super().setUp()
        # [FURN_1118] Corner Desk Left Sit
        self.product13 = self.env.ref("product.product_product_13_product_template")
        # [FURN_8999] Three-Seat Sofa
        self.delivery01 = self.env.ref("product.consu_delivery_01_product_template")
        # [FURN_5555] Cable Management Box
        self.productCM = self.env.ref(
            "stock.product_cable_management_box_product_template"
        )
        # Create a fake route since buy or manufacture routes are not available here
        self.fake_route = self.env["stock.location.route"].create(
            {
                "name": "Fake route -> none",
                "product_selectable": True,
            }
        )

    def test_01_change_type_product_already_used(self):
        def _internal_test(product):
            product.route_ids += self.fake_route
            self.assertTrue(product.route_ids)
            with self.assertRaisesRegex(
                UserError,
                "You can not change the type of a product that was already used",
            ), self.cr.savepoint():
                product.type = "service"
        # unset existing buy route
        self.product13.route_ids = False
        self.assertFalse(self.product13.route_ids)
        self.assertFalse(self.product13.product_variant_id.route_ids)
        _internal_test(self.product13)
        self.assertTrue(self.product13.route_ids)
        self.assertTrue(self.product13.product_variant_id.route_ids)
        _internal_test(self.product13.product_variant_id)

    def test_02_change_consumable_to_service(self):
        def _internal_test(product):
            self.assertFalse(product.route_ids)
            product.route_ids += self.fake_route
            self.assertTrue(self.delivery01.route_ids)
            product.type = "service"
            self.assertFalse(product.route_ids)

        _internal_test(self.delivery01)
        _internal_test(self.delivery01.product_variant_id)

    def test_03_change_stockable_to_service(self):
        def _internal_test(product):
            self.assertFalse(product.route_ids)
            product.route_ids += self.fake_route
            self.assertTrue(product.route_ids)
            product.type = "service"
            self.assertFalse(product.route_ids)

        _internal_test(self.productCM)
        _internal_test(self.productCM.product_variant_id)

    def test_04_create_service_with_route(self):
        myservice = self.env["product.product"].create(
            {
                "name": "My Super Service",
                "type": "service",
                "route_ids": [(4, self.fake_route.id)],
            }
        )
        self.assertFalse(myservice.route_ids)
