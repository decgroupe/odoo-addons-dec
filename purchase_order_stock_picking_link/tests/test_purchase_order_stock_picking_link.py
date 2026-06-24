# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from lxml import etree

from odoo import Command

from odoo.addons.website.tools import MockRequest

from .common import TestPurchaseOrderStockPickingLinkCommon


class TestPurchaseOrderStockPickingLink(TestPurchaseOrderStockPickingLinkCommon):
    """Tests for purchase_order_stock_picking_link module."""

    def test_01_no_outgoing_pickings(self):
        """Verify that a confirmed PO with no linked move_dest_ids has no outgoing
        pickings."""
        po = self._create_purchase_order()
        self.assertEqual(po.outgoing_picking_count, 0)
        self.assertFalse(po.outgoing_picking_ids)

    def test_02_with_outgoing_picking(self):
        """Verify that outgoing_picking_ids reflects the delivery picking linked
        via move_dest_ids on the PO line."""
        po = self._create_purchase_order()
        outgoing_picking, outgoing_move = self._create_outgoing_picking()
        # link outgoing move to the PO line as a destination move
        po_line = po.order_line[0]
        po_line.write({"move_dest_ids": [Command.link(outgoing_move.id)]})
        self.assertEqual(po.outgoing_picking_count, 1)
        self.assertIn(outgoing_picking, po.outgoing_picking_ids)
        # receipt picking must NOT appear in outgoing_picking_ids
        for receipt in po.picking_ids:
            self.assertNotIn(receipt, po.outgoing_picking_ids)

    def test_03_action_single_picking(self):
        """Verify that the action opens the form view directly when there is exactly
        one outgoing picking."""
        po = self._create_purchase_order()
        outgoing_picking, outgoing_move = self._create_outgoing_picking()
        po_line = po.order_line[0]
        po_line.write({"move_dest_ids": [Command.link(outgoing_move.id)]})
        action = po.action_view_outgoing_picking()
        # single picking: res_id must be set and views must include form
        self.assertEqual(action.get("res_id"), outgoing_picking.id)
        view_types = [v_type for _, v_type in action.get("views", [])]
        self.assertIn("form", view_types)

    def test_04_action_multiple_pickings(self):
        """Verify that the action uses a domain filter when there are multiple
        outgoing pickings."""
        po = self._create_purchase_order()
        outgoing_picking1, outgoing_move1 = self._create_outgoing_picking()
        outgoing_picking2, outgoing_move2 = self._create_outgoing_picking()
        po_line = po.order_line[0]
        po_line.write(
            {
                "move_dest_ids": [
                    Command.link(outgoing_move1.id),
                    Command.link(outgoing_move2.id),
                ]
            }
        )
        self.assertEqual(po.outgoing_picking_count, 2)
        action = po.action_view_outgoing_picking()
        # multiple pickings: domain must be set, res_id must be falsy
        self.assertIn("domain", action)
        self.assertFalse(action.get("res_id"))

    def test_05_form_view_fields(self):
        """Verify that outgoing_picking_ids and outgoing_picking_count are present
        in the combined purchase order form view arch."""
        with MockRequest(self.env) as mock:
            # simulate a debug HTTP request so base.group_no_one is active
            mock.session.debug = True
            self.assertTrue(self.env.user.has_group("base.group_no_one"))
            view_info = self.env["purchase.order"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("outgoing_picking_ids", field_names)
        self.assertIn("outgoing_picking_count", field_names)
