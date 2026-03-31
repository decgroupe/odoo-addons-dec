# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockReturnRoutes(TransactionCase):
    """Tests for stock_return_routes module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test fixtures."""
        super().setUpClass()
        # get routes from product_legacy_routes helpers
        cls.mto_route = cls.env["product.template"]._get_mto_route()
        cls.mto_mts_route = cls.env["product.template"]._get_mto_mts_route()
        # get a stock location for unbuild orders
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        # create a storable finished product
        cls.product_finished = cls.env["product.product"].create(
            {
                "name": "Test Finished Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # create a storable component product with MTO route
        cls.product_component = cls.env["product.product"].create(
            {
                "name": "Test Component (MTO)",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.link(cls.mto_route.id)],
            }
        )
        # create a bill of materials for the finished product
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_tmpl_id": cls.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product_component.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )

    def test_01_no_route_change_when_product_has_no_mto(self):
        """No route change for a product without the MTO route."""
        product = self.env["product.product"].create(
            {
                "name": "Product Without MTO",
                "type": "consu",
                "is_storable": True,
            }
        )
        result = product.update_routes_after_return_to_stock("test reason")
        self.assertEqual(result, [])
        self.assertNotIn(self.mto_route, product.product_tmpl_id.route_ids)
        self.assertNotIn(self.mto_mts_route, product.product_tmpl_id.route_ids)

    def test_02_mto_route_replaced_with_mto_mts(self):
        """MTO route is swapped to MTO+MTS when the product returns to stock."""
        product_tmpl = self.product_component.product_tmpl_id
        self.assertIn(self.mto_route, product_tmpl.route_ids)
        self.assertNotIn(self.mto_mts_route, product_tmpl.route_ids)
        result = self.product_component.update_routes_after_return_to_stock(
            "unbuild/001"
        )
        self.assertIn(self.product_component.id, result)
        self.assertNotIn(self.mto_route, product_tmpl.route_ids)
        self.assertIn(self.mto_mts_route, product_tmpl.route_ids)

    def test_03_no_change_when_already_has_mto_mts(self):
        """No route change when the product already has both MTO and MTO+MTS routes."""
        product = self.env["product.product"].create(
            {
                "name": "Product With MTO+MTS",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.link(self.mto_route.id),
                    Command.link(self.mto_mts_route.id),
                ],
            }
        )
        result = product.update_routes_after_return_to_stock("test reason")
        self.assertEqual(result, [])
        # both routes should still be present
        self.assertIn(self.mto_route, product.product_tmpl_id.route_ids)
        self.assertIn(self.mto_mts_route, product.product_tmpl_id.route_ids)

    def test_04_generate_produce_moves_updates_component_routes(self):
        """_generate_produce_moves swaps MTO to MTO+MTS on unbuild components."""
        unbuild = self.env["mrp.unbuild"].create(
            {
                "product_id": self.product_finished.id,
                "product_qty": 1.0,
                "product_uom_id": self.product_finished.uom_id.id,
                "bom_id": self.bom.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_stock.id,
            }
        )
        component_tmpl = self.product_component.product_tmpl_id
        self.assertIn(self.mto_route, component_tmpl.route_ids)
        produce_moves = unbuild._generate_produce_moves()
        self.assertTrue(produce_moves)
        # component route should now be MTO+MTS, not MTO
        self.assertNotIn(self.mto_route, component_tmpl.route_ids)
        self.assertIn(self.mto_mts_route, component_tmpl.route_ids)
        # produce moves should have their move_orig_ids set to the consume lines
        for move in produce_moves:
            self.assertEqual(move.move_orig_ids, unbuild.consume_line_ids)

    def test_05_generate_produce_moves_no_route_change_without_mto(self):
        """_generate_produce_moves does not update routes when component lacks MTO."""
        # create a component without any route
        product_no_mto = self.env["product.product"].create(
            {
                "name": "Component Without MTO",
                "type": "consu",
                "is_storable": True,
            }
        )
        bom_no_mto = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_finished.product_tmpl_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": product_no_mto.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )
        unbuild = self.env["mrp.unbuild"].create(
            {
                "product_id": self.product_finished.id,
                "product_qty": 1.0,
                "product_uom_id": self.product_finished.uom_id.id,
                "bom_id": bom_no_mto.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_stock.id,
            }
        )
        produce_moves = unbuild._generate_produce_moves()
        self.assertTrue(produce_moves)
        # route should remain unchanged
        self.assertNotIn(self.mto_mts_route, product_no_mto.product_tmpl_id.route_ids)
