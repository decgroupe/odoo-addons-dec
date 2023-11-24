# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2023

from odoo.addons.stock_actions_tests.tests.common import TestStockActionTestsCommon
from odoo.exceptions import UserError


class TestStockActionTests(TestStockActionTestsCommon):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super(TestStockActionTests, self).setUp()

    def test_01_no_route(self):
        move = self._create_mto_customer_move()
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [],
                    )
                ]
            }
        )
        with self.assertRaisesRegex(
            UserError, "No rule has been found to replenish.*"
        ), self.cr.savepoint():
            move.action_confirm()

    def test_02_mto_route(self):
        move = self._create_mto_customer_move()
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            self.route_mto.id,
                        ],
                    )
                ]
            }
        )
        with self.assertRaisesRegex(
            UserError, "No rule has been found to replenish.*"
        ), self.cr.savepoint():
            move.action_confirm()

    def test_03_mto_plus_buy_routes_nosupplier(self):
        move = self._create_mto_customer_move()
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            self.route_mto.id,
                            self.route_buy.id,
                        ],
                    )
                ]
            }
        )
        with self.assertRaisesRegex(
            UserError,
            "There is no matching vendor price to generate the purchase order.*",
        ), self.cr.savepoint():
            move.action_confirm()

    def test_04_mto_plus_manufacture_routes_nobom(self):
        move = self._create_mto_customer_move()
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            self.route_mto.id,
                            self.route_manufacture.id,
                        ],
                    )
                ]
            }
        )
        with self.assertRaisesRegex(
            UserError,
            "There is no Bill of Material of type manufacture or kit found.*",
        ), self.cr.savepoint():
            move.action_confirm()

    def test_05_mto_plus_buy_routes(self):
        move = self._create_mto_customer_move()
        vendor = self.env["res.partner"].create({"name": "Nice Vendor"})
        supplier_info = self.env["product.supplierinfo"].create(
            {
                "name": vendor.id,
                "price": 50,
            }
        )
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            self.route_mto.id,
                            self.route_buy.id,
                        ],
                    )
                ],
                "seller_ids": [(6, 0, [supplier_info.id])],
            }
        )
        # move should be cancellable from UI while not confirmed
        self.assertTrue(move.is_cancellable)
        move.action_confirm()
        # move should not be cancellable now from UI
        self.assertEqual(move.state, "waiting")
        self.assertFalse(move.is_cancellable)
        # check that this move is now linked to a purchase order
        self.assertTrue(move.created_purchase_line_id)

    def test_06_mto_plus_manufacture_routes(self):
        move = self._create_mto_customer_move()
        self.product.write(
            {
                "route_ids": [
                    (
                        6,
                        0,
                        [
                            self.route_mto.id,
                            self.route_manufacture.id,
                        ],
                    )
                ]
            }
        )
        bom_id = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_id": self.product.id,
                "product_uom_id": self.unit_uom_id.id,
                "sequence": 1,
            }
        )
        # move should be cancellable from UI while not confirmed
        self.assertTrue(move.is_cancellable)
        move.action_confirm()
        # move should not be cancellable now from UI
        self.assertEqual(move.state, "waiting")
        self.assertFalse(move.is_cancellable)
        # check that a move linked to a production order has been created
        self.assertEqual(len(move.move_orig_ids), 1)
        production_move = move.move_orig_ids[0]
        self.assertEqual(production_move.state, "draft")
        self.assertTrue(production_move.production_id)
