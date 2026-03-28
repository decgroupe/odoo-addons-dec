# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestMrpMtsMto(TransactionCase):
    """Tests for mrp_mts_mto module.

    Verify that _adjust_procure_method correctly handles the split_procurement
    rule for raw material moves in manufacturing orders.
    """

    @classmethod
    def setUpClass(cls):
        """Set up shared test fixtures."""
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        # enable MTS+MTO management on the warehouse
        cls.warehouse.mto_mts_management = True
        # routes
        cls.route_mto = cls.warehouse.mto_pull_id.route_id
        cls.route_mto.active = True
        cls.route_mto_mts = cls.warehouse.mts_mto_rule_id.route_id
        # create a fake route since buy route is not available here
        # cls.route_buy = cls.warehouse.buy_pull_id.route_id # --> need `purchase`
        cls.route_fakebuy = cls.env["stock.route"].create(
            {
                "name": "Buy (Fake)",
                "product_selectable": True,
            }
        )
        _route_fakebuy_rule0 = cls.env["stock.rule"].create(
            {
                "route_id": cls.route_fakebuy.id,
                "name": "Buy Rule (simple transfert)",
                "action": "pull",
                # San Francisco: Receipts
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                # Partner Locations/Vendors
                "location_src_id": cls.env.ref("stock.stock_location_suppliers").id,
                # WH/Stock
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "location_dest_from_rule": True,
                "procure_method": "make_to_stock",
                "warehouse_id": cls.warehouse.id,
                "company_id": cls.warehouse.company_id.id,
            }
        )


        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        # create the raw material product with MTS+MTO route
        cls.raw_product = cls.env["product.product"].create(
            {
                "name": "Test Raw Material",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.link(cls.route_mto_mts.id),
                    Command.link(cls.route_fakebuy.id),
                ],
            }
        )
        # create the finished product
        cls.finished_product = cls.env["product.product"].create(
            {
                "name": "Test Finished Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        # create a bill of materials linking finished to raw
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.finished_product.id,
                "product_tmpl_id": cls.finished_product.product_tmpl_id.id,
                "product_uom_id": cls.uom_unit.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.raw_product.id,
                            "product_qty": 5.0,
                        }
                    ),
                ],
            }
        )

    def _create_quant(self, qty):
        """Create a stock quant to put raw material stock in the warehouse."""
        self.env["stock.quant"].create(
            {
                "location_id": self.stock_location.id,
                "product_id": self.raw_product.id,
                "quantity": qty,
            }
        )

    def _create_and_confirm_mo(self, qty=5.0):
        """Create and confirm a manufacturing order for the finished product."""
        mo = self.env["mrp.production"].create(
            {
                "product_id": self.finished_product.id,
                "product_qty": qty,
                "product_uom_id": self.uom_unit.id,
                "bom_id": self.bom.id,
            }
        )
        mo.action_confirm()
        return mo

    def test_01_no_stock_becomes_make_to_order(self):
        """Raw material move becomes make_to_order when no stock is available."""
        mo = self._create_and_confirm_mo(qty=5.0)
        raw_move = mo.move_raw_ids.filtered(lambda m: m.product_id == self.raw_product)
        self.assertEqual(len(raw_move), 1)
        self.assertEqual(raw_move.procure_method, "make_to_order")

    def test_02_full_stock_stays_make_to_stock(self):
        """Raw material move stays make_to_stock when enough stock is available."""
        # put more stock than needed (25.0 needed, 50.0 available)
        self._create_quant(50.0)
        mo = self._create_and_confirm_mo(qty=5.0)
        raw_move = mo.move_raw_ids.filtered(lambda m: m.product_id == self.raw_product)
        self.assertEqual(len(raw_move), 1)
        self.assertEqual(raw_move.procure_method, "make_to_stock")
        self.assertEqual(raw_move.product_uom_qty, 25.0)

    def test_03_partial_stock_splits_move(self):
        """Raw material move is split when only partial stock is available."""
        # put 10.0 units available; 25.0 needed -> 10.0 MTS, 15.0 MTO
        self._create_quant(10.0)
        mo = self._create_and_confirm_mo(qty=5.0)
        raw_moves = mo.move_raw_ids.filtered(lambda m: m.product_id == self.raw_product)
        # after split there must be two raw moves
        self.assertEqual(len(raw_moves), 2)
        mts_move = raw_moves.filtered(lambda m: m.procure_method == "make_to_stock")
        mto_move = raw_moves.filtered(lambda m: m.procure_method == "make_to_order")
        self.assertEqual(len(mts_move), 1)
        self.assertEqual(len(mto_move), 1)
        self.assertAlmostEqual(mts_move.product_uom_qty, 10.0, places=4)
        self.assertAlmostEqual(mto_move.product_uom_qty, 15.0, places=4)
        self.assertAlmostEqual(
            mts_move.product_uom_qty + mto_move.product_uom_qty, 25.0, places=4
        )
