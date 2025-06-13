# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jun 2025

from odoo import Command

from odoo.addons.stock_actions_tests.tests.common import TestStockActionTestsCommon


class TestMrpPurchaseProgress(TestStockActionTestsCommon):
    """Test the purchase progress computation on manufacturing orders with
    components to purchase."""

    def _get_po(self, production):
        move_ids = production.procurement_group_id.stock_move_ids
        purchase_order_ids = (
            move_ids.created_purchase_line_ids.order_id
            | move_ids.move_orig_ids.purchase_line_id.order_id
        )
        return purchase_order_ids

    def _get_po_line(self, purchase_orders, product):
        res = purchase_orders.order_line.filtered(lambda m: m.product_id == product)
        self.assertTrue(res)
        self.assertEqual(len(res), 1)
        return res

    def setUp(self):
        super().setUp()

    def test_01_purchase_progress(self):
        # create two new vendors
        vendor_1 = self.env["res.partner"].create(
            {"name": "Vendor 1", "supplier_rank": 1}
        )
        vendor_2 = self.env["res.partner"].create(
            {"name": "Vendor 2", "supplier_rank": 1}
        )
        # create two purchasable products with MTO route + BUY route
        p1 = self.env["product.product"].create(
            {
                "name": "Test Product 1",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set([self.route_mto.id, self.route_buy.id])],
                "seller_ids": [
                    Command.create(
                        {"partner_id": vendor_1.id, "min_qty": 0, "price": 10.0}
                    )
                ],
            }
        )
        p2 = self.env["product.product"].create(
            {
                "name": "Test Product 2",
                "type": "consu",
                "is_storable": True,
                "route_ids": [Command.set([self.route_mto.id, self.route_buy.id])],
                "seller_ids": [
                    Command.create(
                        {"partner_id": vendor_2.id, "min_qty": 0, "price": 20.0}
                    )
                ],
            }
        )
        # create a manufacturable product
        final_product = self.env["product.product"].create(
            {
                "name": "Finished product",
                "type": "consu",
                "is_storable": True,
                "route_ids": [
                    Command.link(self.route_manufacture.id),
                    Command.link(self.route_mto.id),
                ],
            }
        )
        # bom includes the two purchasable products
        final_product_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": final_product.product_tmpl_id.id,
                "product_uom_id": final_product.uom_id.id,
                "product_qty": 1,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": p1.id,
                            "product_uom_id": p1.uom_id.id,
                            "product_qty": 2,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": p2.id,
                            "product_uom_id": p2.uom_id.id,
                            "product_qty": 3,
                        }
                    ),
                ],
            }
        )
        # create a first empty manufacturing order
        production = self.env["mrp.production"].create(
            {
                "product_id": final_product.id,
                "product_uom_id": final_product.uom_id.id,
                "product_qty": 1,
                "bom_id": False,
            }
        )
        self.assertFalse(production.move_raw_ids, "No raw moves should exist yet.")
        self.assertFalse(production.kanban_show_purchase_progress)
        # plan the manufacturing order to generate raw moves
        production = self.env["mrp.production"].create(
            {
                "product_id": final_product.id,
                "product_uom_id": final_product.uom_id.id,
                "product_qty": 1,
                "bom_id": final_product_bom.id,
            }
        )
        self.assertEqual(len(production.move_raw_ids), 2)
        self.assertFalse(production.kanban_show_purchase_progress)
        # check stage before and after confirmation
        self.assertEqual(production.stage_id, self.env.ref("mrp_stage.stage_draft"))
        production.action_confirm()
        self.assertEqual(production.stage_id, self.env.ref("mrp_stage.stage_confirmed"))
        # check current purchase progress
        production.action_update_purchase_progress()
        self.assertFalse(production.kanban_show_purchase_progress)
        self.assertEqual(production.purchase_progress, 0)
        # check purchase orders created
        purchase_order = self._get_po(production)
        self.assertEqual(len(purchase_order), 2)
        # receive only one purchase order
        po_line_1 = self._get_po_line(purchase_order, p1)
        self.assertEqual(po_line_1.product_qty, 2)
        purchase_order_1 = po_line_1.order_id
        purchase_order_1.button_confirm()
        picking_1 = purchase_order_1.picking_ids
        self.assertEqual(len(picking_1), 1)
        for move in picking_1.move_ids:
            move._set_quantity_done(move.product_uom_qty)
        picking_1.button_validate()
        # update and check purchase progress
        production.action_update_purchase_progress()
        self.assertEqual(production.purchase_progress, 50)
        # receive the second purchase order
        po_line_2 = self._get_po_line(purchase_order, p2)
        self.assertEqual(po_line_2.product_qty, 3)
        purchase_order_2 = po_line_2.order_id
        purchase_order_2.button_confirm()
        picking_2 = purchase_order_2.picking_ids
        self.assertEqual(len(picking_2), 1)
        for move in picking_2.move_ids:
            move._set_quantity_done(move.product_uom_qty)
        picking_2.button_validate()
        # final update and check purchase progress
        production.action_update_purchase_progress()
        self.assertEqual(production.purchase_progress, 100)
