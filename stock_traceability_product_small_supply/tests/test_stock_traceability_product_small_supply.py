# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from odoo.addons.stock_traceability.tests.common import TestStockTraceabilityBase


class TestStockTraceabilityProductSmallSupply(TestStockTraceabilityBase):
    """Tests for stock_traceability_product_small_supply module."""

    def test_01_move_pre_header_small_supply_stockable(self):
        """Tests that stockable small-supply products use a dedicated header."""
        product = self.env["product.product"].create(
            {
                "name": "Small Supply Product",
                "type": "consu",
                "is_storable": True,
                "small_supply": True,
            }
        )
        move = self._create_picking_move(
            product,
            self.picking_out,
            name="Small Supply Move",
            product_uom_qty=1,
        )
        self.assertEqual(move._get_pre_header(), "⛽Small Supply")

    def test_02_move_pre_header_small_supply_non_storable(self):
        """Tests that non-storable products keep `stock_traceability` fallback
        header."""
        product = self.env["product.product"].create(
            {
                "name": "Non-Storable Small Supply Product",
                "type": "consu",
                "is_storable": False,
                "small_supply": True,
            }
        )
        move = self._create_picking_move(
            product,
            self.picking_out,
            name="Non-Storable Small Supply Move",
            product_uom_qty=1,
        )
        self.assertEqual(move._get_pre_header(), "🧃Goods")

    def test_03_move_pre_header_small_supply_service(self):
        """Tests that service products keep `stock_traceability` fallback header."""
        product = self.env["product.product"].create(
            {
                "name": "Service Small Supply Product",
                "type": "service",
                "small_supply": True,
            }
        )
        move = self._create_picking_move(
            product,
            self.picking_out,
            name="Service Small Supply Move",
            product_uom_qty=1,
        )
        self.assertEqual(move._get_pre_header(), "🛎️Service")

    def test_04_move_pick_status_small_supply_stockable(self):
        """Tests that pick status embeds the dedicated small-supply header."""
        product = self.env["product.product"].create(
            {
                "name": "Small Supply Pick Status Product",
                "type": "consu",
                "is_storable": True,
                "small_supply": True,
            }
        )
        move = self._create_picking_move(
            product,
            self.picking_out,
            name="Small Supply Pick Status Move",
            product_uom_qty=1,
        )
        self.assertEqual(
            move.get_pick_status(html=False),
            "⛽Small Supply\n📦Stock 🏳️New",
        )
