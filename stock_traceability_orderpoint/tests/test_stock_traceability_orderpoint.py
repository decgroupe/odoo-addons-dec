# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026

from odoo import Command
from odoo.tests.common import TransactionCase


class TestStockTraceabilityOrderpoint(TransactionCase):
    """Tests stock.warehouse.orderpoint traceability with manufacturing orders."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Picking = cls.env["stock.picking"]
        cls.Move = cls.env["stock.move"]
        cls.Production = cls.env["mrp.production"]
        cls.Product = cls.env["product.product"]
        cls.Orderpoint = cls.env["stock.warehouse.orderpoint"]
        cls.StockLocation = cls.env["stock.location"]
        cls.Route = cls.env["stock.route"]
        cls.Bom = cls.env["mrp.bom"]
        cls.BomLine = cls.env["mrp.bom.line"]
        cls.PurchaseLine = cls.env["purchase.order.line"]
        cls.ProcurementGroup = cls.env["procurement.group"]

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.picking_type_in = cls.warehouse.in_type_id
        cls.picking_type_out = cls.warehouse.out_type_id

        cls.stock_loc = cls.warehouse.lot_stock_id
        route_manuf = cls.warehouse.manufacture_pull_id.route_id
        route_buy = cls.warehouse.buy_pull_id.route_id

        # create vendors
        cls.vendor_1 = cls.env["res.partner"].create(
            {"name": "Vendor 1", "supplier_rank": 1}
        )

        # prepare products
        cls.product_to_manufacture = cls.Product.create(
            {
                "name": "Test Product",
                "route_ids": [Command.set(route_manuf.ids)],
                "type": "consu",
                "is_storable": True,
            }
        )
        component_for_product = cls.Product.create(
            {
                "name": "Test component",
                "route_ids": [Command.set(route_buy.ids)],
                "type": "consu",
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.vendor_1.id,
                            "min_qty": 1.0,
                            "price": 10.0,
                        }
                    )
                ],
            }
        )

        # create Bill of Materials
        cls.bom_1 = cls.Bom.create(
            {
                "product_id": cls.product_to_manufacture.id,
                "product_tmpl_id": cls.product_to_manufacture.product_tmpl_id.id,
                "product_uom_id": cls.product_to_manufacture.uom_id.id,
                "product_qty": 1.0,
                "bom_line_ids": [
                    Command.clear(),
                    Command.create(
                        {
                            "product_id": component_for_product.id,
                            "product_qty": 1.0,
                        }
                    ),
                ],
            }
        )

        # create Orderpoint for product to manufacture
        cls.orderpoint_ptm = cls.Orderpoint.create(
            {
                "name": "OP_XYZ_1",
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "product_id": cls.product_to_manufacture.id,
                "product_min_qty": 10.0,
                "product_max_qty": 50.0,
                "product_uom": cls.product_to_manufacture.uom_id.id,
            }
        )
        # create Orderpoint for component
        cls.orderpoint_component = cls.Orderpoint.create(
            {
                "name": "OP_XYZ_2",
                "warehouse_id": cls.warehouse.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "product_id": component_for_product.id,
                "product_min_qty": 1.0,
                "product_max_qty": 10.0,
                "product_uom": component_for_product.uom_id.id,
            }
        )
        # cls.ProcurementGroup.run_scheduler()

    def setUp(self):
        super().setUp()

    def _create_picking_and_confirm(self):
        current_production_ids = self.Production.search([])
        current_purchase_line_ids = self.PurchaseLine.search([])
        # create outgoing picking
        picking_out = self.Picking.create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        # create move for our "product" from stock to customer, that should trigger
        # a manufacturing order from orderpoint
        move_out = self.Move.create(
            {
                "name": "Move Out",
                "product_id": self.product_to_manufacture.id,
                "product_uom_qty": 10,
                "product_uom": self.product_to_manufacture.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": picking_out.location_id.id,
                "location_dest_id": picking_out.location_dest_id.id,
            }
        )
        picking_out.action_confirm()
        # ensure that a production order has been created by orderpoint
        new_production_ids = self.Production.search([]) - current_production_ids
        # ensure that a purchase order line has been created by orderpoint
        new_purchase_line_ids = self.PurchaseLine.search([]) - current_purchase_line_ids
        return move_out, new_production_ids, new_purchase_line_ids

    def test_01_created_items_by_orderpoint(self):
        """Test that manufacturing orders and purchase order lines created by
        orderpoints are properly linked on stock moves.
        """
        (
            move_out,
            new_production_ids,
            new_purchase_line_ids,
        ) = self._create_picking_and_confirm()
        self.assertEqual(len(new_production_ids), 1)
        # check that move has linked production order created by orderpoint
        self.assertEqual(move_out.orderpoint_created_production_ids, new_production_ids)
        self.assertEqual(len(new_purchase_line_ids), 1)
        # check that component move has linked purchase order line created by orderpoint
        component_move = new_production_ids.move_raw_ids[0]
        self.assertEqual(
            component_move.orderpoint_created_purchase_line_ids, new_purchase_line_ids
        )

    def test_02_mts_status_messages(self):
        """Test that manufacturing orders and purchase order lines created by
        orderpoints are properly reported in MTS status messages.
        """
        (
            move_out,
            new_production_ids,
            new_purchase_line_ids,
        ) = self._create_picking_and_confirm()
        self.assertEqual(len(new_production_ids), 1)
        self.assertEqual(len(new_purchase_line_ids), 1)
        # check mts status messages for production order move
        mts_status_msgs = move_out._get_mts_status(html=False)
        mts_status_msg = False
        for msg in mts_status_msgs:
            if new_production_ids.name in msg:
                mts_status_msg = msg
                break
        self.assertEqual(
            f"♻️⮡ 🔧{new_production_ids.name} 🏳️Confirmed",
            mts_status_msg,
        )
        # check mts status messages for purchase order move
        component_move = new_production_ids.move_raw_ids[0]
        mts_status_msgs = component_move._get_mts_status(html=False)
        mts_status_msg = False
        for msg in mts_status_msgs:
            if new_purchase_line_ids.order_id.name in msg:
                mts_status_msg = msg
                break
        self.assertEqual(
            f"♻️⮡ 🛒{new_purchase_line_ids.order_id.name} 🏳️RFQ",
            mts_status_msg,
        )

    def test_03_action_view_created_items(self):
        """Test that action_view_created_item method properly returns actions
        to view manufacturing orders and purchase order lines created by
        orderpoints.
        """
        (
            move_out,
            new_production_ids,
            new_purchase_line_ids,
        ) = self._create_picking_and_confirm()
        self.assertEqual(len(new_production_ids), 1)
        self.assertEqual(len(new_purchase_line_ids), 1)
        # check action to view production order from move
        action = move_out.action_view_created_item()
        self.assertEqual(action["res_model"], "mrp.production")
        self.assertEqual(action["res_id"], new_production_ids.id)
        # check action to view purchase order line from component move
        component_move = new_production_ids.move_raw_ids[0]
        action = component_move.action_view_created_item()
        self.assertEqual(action["res_model"], "purchase.order.line")
        self.assertEqual(action["res_id"], new_purchase_line_ids.id)

    def test_04_is_action_view_created_items_visible(self):
        """Test that is_action_view_created_item_visible method properly
        indicates if there are manufacturing orders and purchase order lines
        created by orderpoints linked to the stock moves.
        """
        (
            move_out,
            new_production_ids,
            new_purchase_line_ids,
        ) = self._create_picking_and_confirm()
        self.assertEqual(len(new_production_ids), 1)
        self.assertEqual(len(new_purchase_line_ids), 1)
        # check visibility for production order move
        self.assertTrue(move_out.is_action_view_created_item_visible())
        # check visibility for component move
        component_move = new_production_ids.move_raw_ids[0]
        self.assertTrue(component_move.is_action_view_created_item_visible())

    def test_05_no_created_items(self):
        """Test that stock moves not linked to manufacturing orders or purchase
        order lines created by orderpoints behave correctly.
        """
        # create a simple stock move not linked to orderpoints
        move = self.Move.create(
            {
                "name": "Simple Move",
                "product_id": self.product_to_manufacture.id,
                "product_uom_qty": 5,
                "product_uom": self.product_to_manufacture.uom_id.id,
                "location_id": self.stock_loc.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        # check that no production order or purchase order line is linked
        self.assertFalse(move.orderpoint_created_production_ids)
        self.assertFalse(move.orderpoint_created_purchase_line_ids)
        # check that no orderpoint MTS status messages are returned (use "♻️" as
        # indicator)
        mts_status_msgs = move._get_mts_status(html=False)
        found = False
        for msg in mts_status_msgs:
            if "♻️" in msg:
                found = True
                break
        self.assertFalse(found)
        # check that action_view_created_item returns False
        action = move.action_view_created_item()
        self.assertFalse(action)
        # check that is_action_view_created_item_visible returns False
        self.assertFalse(move.is_action_view_created_item_visible())

    def test_06_orderpoint_head_desc(self):
        """Test get_head_desc method of stock.warehouse.orderpoint."""
        head, desc = self.orderpoint_ptm.get_head_desc()
        self.assertEqual(head, "🧮OP_XYZ_1")
        self.assertEqual(desc, "10.0 ≤ 𝜕 ≤ 50.0 ↗ ×1.0")
        head, desc = self.orderpoint_component.get_head_desc()
        self.assertEqual(head, "🧮OP_XYZ_2")
        self.assertEqual(desc, "1.0 ≤ 𝜕 ≤ 10.0 ↗ ×1.0")
