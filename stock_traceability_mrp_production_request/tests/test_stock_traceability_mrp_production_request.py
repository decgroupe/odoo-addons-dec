# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.addons.stock_traceability_mrp.tests.common import (
    TestStockTraceabilityMrpBase,
)

from ..models.mrp_production_request import PRODUCTION_REQUEST_STATE_SYMBOLS


class TestStockTraceabilityMrpProductionRequest(TestStockTraceabilityMrpBase):
    """Tests for stock_traceability_mrp_production_request module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()

    def setUp(self):
        """Set up test fixtures including a production request and a raw move."""
        super().setUp()
        self.production_request = self.env["mrp.production.request"].create(
            {
                "product_id": self.manufacturable_product.id,
                "product_qty": 1.0,
                "product_uom_id": self.manufacturable_product.uom_id.id,
                "bom_id": self.bom.id,
            }
        )
        # create a production order to get a raw component move for testing
        self.test_production = self.env["mrp.production"].create(
            {
                "product_id": self.manufacturable_product.id,
                "product_qty": 1,
                "product_uom_id": self.manufacturable_product.uom_id.id,
            }
        )
        self.test_move = self.test_production.move_raw_ids

    def test_01_production_request_states(self):
        """Test that all hard-coded production request states have a symbol match."""
        self._check_states(PRODUCTION_REQUEST_STATE_SYMBOLS, "mrp.production.request")

    def test_02_production_request_head_description(self):
        """Test get_head_desc for all production request state transitions."""
        request = self.production_request
        head, desc = request.get_head_desc()
        self.assertEqual(head, f"⚙️{request.name}")
        self.assertEqual(desc, "🏳️Draft")
        # transition to "to_approve"
        request.button_to_approve()
        head, desc = request.get_head_desc()
        self.assertEqual(head, f"⚙️{request.name}")
        self.assertEqual(desc, "⏳To Be Approved")
        # transition to "approved"
        request.button_approved()
        head, desc = request.get_head_desc()
        self.assertEqual(head, f"⚙️{request.name}")
        self.assertEqual(desc, "🚧Approved")
        # transition to "done"
        request.button_done()
        head, desc = request.get_head_desc()
        self.assertEqual(head, f"⚙️{request.name}")
        self.assertEqual(desc, "✅Done")

    def test_03_move_mto_status_with_production_request(self):
        """Test _get_mto_status override when a production request is linked to
        the move: it must return the request head/desc instead of the fallback.
        """
        # without production request: the request symbol must not appear
        status_no_req = self.test_move._get_mto_status(html=False)
        self.assertFalse(any("⚙️" in s for s in status_no_req))
        # link the production request to the move
        self.test_move.created_mrp_production_request_id = self.production_request
        # with production request: request head/desc must be the sole item
        status_with_req = self.test_move._get_mto_status(html=False)
        self.assertEqual(len(status_with_req), 1)
        expected = f"⚙️{self.production_request.name} 🏳️Draft"
        self.assertEqual(status_with_req[0], expected)

    def test_04_move_action_view_created_item_without_mo(self):
        """Test action_view_created_item opens the production request form when
        the request has no linked manufacturing orders.
        """
        self.test_move.created_mrp_production_request_id = self.production_request
        self.assertFalse(self.production_request.mrp_production_ids)
        action = self.test_move.action_view_created_item()
        self.assertTrue(action)
        self.assertEqual(action.get("res_id"), self.production_request.id)

    def test_05_move_action_view_created_item_with_mo(self):
        """Test action_view_created_item opens MO view when the production
        request has at least one linked manufacturing order.
        """
        # link the test production to the request so mrp_production_ids is populated
        self.test_production.mrp_production_request_id = self.production_request
        self.test_move.created_mrp_production_request_id = self.production_request
        self.assertTrue(self.production_request.mrp_production_ids)
        action = self.test_move.action_view_created_item()
        self.assertTrue(action)
        # the action should point to the linked manufacturing order
        self.assertEqual(action.get("res_id"), self.test_production.id)

    def test_06_action_view_created_item_visible(self):
        """Test action_view_created_item_visible is True only when a production
        request is linked to the move.
        """
        # no production request linked: visibility must be false
        self.assertFalse(self.test_move.created_mrp_production_request_id)
        self.assertFalse(self.test_move.action_view_created_item_visible)
        # link production request: visibility must become true
        self.test_move.created_mrp_production_request_id = self.production_request
        self.assertTrue(self.test_move.action_view_created_item_visible)
