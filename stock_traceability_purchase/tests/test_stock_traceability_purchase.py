# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import logging

import freezegun

from odoo import Command
from odoo.tests.common import new_test_user

from odoo.addons.stock_traceability.tests.common import TestStockTraceabilityBase

from ..models.purchase_order import PURCHASE_STATE_SYMBOLS

_logger = logging.getLogger(__name__)


class TestStockTraceabilityPurchase(TestStockTraceabilityBase):
    """Tests for Stock Traceability module."""

    def _create_purchase_order(self, partner, product, qty=10):
        return self.env["purchase.order"].create(
            {
                "partner_id": partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_qty": qty,
                            "product_uom": product.uom_id.id,
                            "price_unit": 15.0,
                        },
                    )
                ],
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test Supplier"})
        # add supplier to our product
        self.product.seller_ids = [
            Command.create({"partner_id": self.partner.id, "min_qty": 1, "price": 10.0})
        ]

    def test_01_purchase_states(self):
        """Tests that all hard-coded purchase states have a symbol match"""
        self._check_states(PURCHASE_STATE_SYMBOLS, "purchase.order")

    def test_02_purchase_head_description(self):
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        purchase_user = new_test_user(
            self.env,
            login="action_view-user",
            groups="purchase.group_purchase_user",
            context=ctx,
        )
        purchase_order = (
            self.env["purchase.order"]
            .with_user(purchase_user)
            .create(
                {
                    "partner_id": self.env.ref("base.res_partner_12").id,
                    "order_line": [
                        Command.create(
                            {
                                "product_id": self.env.ref(
                                    "product.product_product_5"
                                ).id,
                                "product_qty": 10,
                                "product_uom": self.env.ref("uom.product_uom_unit").id,
                                "price_unit": 15.0,
                            },
                        )
                    ],
                }
            )
        )
        po_name = f"🛒{purchase_order.name}"
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "🏳️RFQ")
        # change state to approved
        self.env.company.write(
            {
                "po_double_validation": "two_step",
                # require validation above 1.00 currency unit
                "po_double_validation_amount": 1.00,
            }
        )
        purchase_order.button_confirm()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "⏳To Approve")
        # approve and confirm
        purchase_order.with_user(self.env.user).button_approve()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "💲Purchase Order")
        # change state to done
        purchase_order.button_done()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "✅Locked")
        # change state to cancelled
        purchase_order.button_cancel()
        head, desc = purchase_order.order_line[0].get_head_desc()
        self.assertEqual(head, po_name)
        self.assertEqual(desc, "❌Cancelled")

    def test_03_create_purchase_from_picking_out(self):
        # add some move lines for our test product
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
            procure_method="make_to_order",  # to force procurement
        )
        self.picking_out.action_confirm()
        # ensure this move is not linked as incoming to any purchase line
        self.assertFalse(move.purchase_line_id)
        # ensure this move has no origin moves
        self.assertFalse(move.move_orig_ids)
        # a purchase line should have been created and linked to the move
        self.assertEqual(len(move.created_purchase_line_ids), 1)
        # rename purchase order
        order_id = move.created_purchase_line_ids.order_id
        order_id.name = "PO/TEST/03"
        # test status
        self.assertEqual(
            move.pick_status,
            '<div class="d_move d_move_waiting"><ul><li>➕Goods</li>'
            "<li>🛒PO/TEST/03 <small>🏳️RFQ</small></li></ul></div>",
        )
        # test plain text version
        status = move.get_pick_status(html=False)
        self.assertEqual(status, "➕Goods\n🛒PO/TEST/03 🏳️RFQ")
        # cancel order and check updated status
        order_id.button_cancel()
        status = move.get_pick_status(html=False)
        self.assertEqual(
            status, "➕Goods\n📦Stock ⏳Waiting Availability\n♻️PO/canceled"
        )

    @freezegun.freeze_time("2017-01-12")
    def test_04_create_picking_in_from_purchase(self):
        # add some move lines for our test product
        move = self._create_picking_move(
            self.product,
            self.picking_out,
            name="Test Move",
            product_uom_qty=10,
            procure_method="make_to_order",  # to force procurement
        )
        self.picking_out.action_confirm()
        # ensure this move is not linked as incoming to any purchase line
        self.assertFalse(move.purchase_line_id)
        # ensure this move has no origin moves
        self.assertFalse(move.move_orig_ids)
        # a purchase line should have been created and linked to the move
        self.assertEqual(len(move.created_purchase_line_ids), 1)
        po_line = move.created_purchase_line_ids
        # rename purchase order
        order_id = po_line.order_id
        order_id.name = "PO/TEST/04"
        # confirm order and check created picking
        order_id.button_confirm()
        pickings = order_id.picking_ids
        self.assertEqual(len(pickings), 1)
        # rename picking
        pickings.name = "WH/IN/TEST/04"
        # `created_purchase_line_ids` is automatically unset once the purchase line is
        # linked to the incoming move with `purchase_line_id`
        self.assertFalse(move.created_purchase_line_ids)
        # check that both are the same
        self.assertEqual(move.move_orig_ids, pickings.move_ids)
        # and that the purchase line is correctly linked to the incoming move
        self.assertEqual(po_line, pickings.move_ids.purchase_line_id)
        # test status
        self.assertEqual(
            move.pick_status,
            '<div class="d_move d_move_waiting"><ul><li>➕Goods</li>'
            "<li>🛒PO/TEST/04 <small>💲Purchase Order</small></li>"
            "<li>🚚 WH/IN/TEST/04 <small>2017-01-12</small></li>"
            "<li>📦Stock <small>✳️Available</small></li>"
            "<li>📤📋 <small>PO/TEST/04</small></li></ul></div>",
        )
        # test plain text version
        status = move.get_pick_status(html=False)
        self.assertEqual(
            status,
            "➕Goods\n🛒PO/TEST/04 💲Purchase Order\n🚚 WH/IN/TEST/04 2017-01-12\n"
            "📦Stock ✳️Available\n📤📋 PO/TEST/04",
        )
        # test status for incoming move
        move_in = move.move_orig_ids
        self.assertEqual(
            move_in.pick_status,
            '<div class="d_move d_move_assigned"><ul><li>➕Goods</li>'
            "<li>📦Stock <small>✳️Available</small></li></ul></div>",
        )
        # test plain text version
        status = move_in.get_pick_status(html=False)
        self.assertEqual(
            status,
            "➕Goods\n📦Stock ✳️Available",
        )

    def test_05_archive_created_purchase_lines(self):
        """Test archiving from `stock.move` create/write, since real archiving is
        commonly done in `purchase.order.line` write when `move_dest_ids` is updated.
        """
        purchase_order = self._create_purchase_order(self.partner, self.product)
        purchase_order.name = "PO/TEST/05/01"
        po_line = purchase_order.order_line
        self.assertTrue(len(po_line), 1)
        # create a move linked to the purchase line with `created_purchase_line_ids`
        solo_move = self._create_move(
            self.product,
            self.picking_out.location_id,
            self.picking_out.location_dest_id,
            name="Test Move",
            product_uom_qty=10,
            created_purchase_line_ids=[Command.link(po_line.id)],
        )
        self.assertTrue(solo_move.created_purchase_lines_archive)
        # duplicate the purchase order
        purchase_order2 = purchase_order.copy({"name": "PO/TEST/05/02"})
        # the same move must now be linked to both purchase orders
        self.assertEqual(len(solo_move.created_purchase_line_ids), 2)
        # create a new purchase order
        purchase_order3 = self._create_purchase_order(self.partner, self.product)
        purchase_order3.name = "PO/TEST/05/03"
        po_line3 = purchase_order3.order_line
        # manualy link this line to our existing move with `created_purchase_line_ids`
        solo_move.created_purchase_line_ids = [Command.link(po_line3.id)]
        # the same move must now be linked to 3 purchase orders
        self.assertEqual(len(solo_move.created_purchase_line_ids), 3)
        # keep current archives
        archive_pre = list(solo_move.created_purchase_lines_archive.values())
        # cancel purchase orders
        purchase_order.button_cancel()
        self.assertEqual(len(solo_move.created_purchase_line_ids), 2)
        purchase_order2.button_cancel()
        self.assertEqual(len(solo_move.created_purchase_line_ids), 1)
        purchase_order3.button_cancel()
        self.assertEqual(len(solo_move.created_purchase_line_ids), 0)
        # check that the 3 purchase order names are archived
        archive_post = list(solo_move.created_purchase_lines_archive.values())
        self.assertEqual(archive_pre, archive_post)
        self.assertIn("PO/TEST/05/01", archive_post)
        self.assertIn("PO/TEST/05/02", archive_post)
        self.assertIn("PO/TEST/05/03", archive_post)
