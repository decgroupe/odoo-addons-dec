# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from unittest.mock import patch

from lxml import etree

from odoo import Command

from .common import TestMrpTraceabilityCommon


class TestMrpTraceability(TestMrpTraceabilityCommon):
    """Tests for mrp_traceability module."""

    def test_01_conv_dest_ids_linked_to_finished_moves(self):
        """Verify raw moves have move_conv_dest_ids pointing to finished moves."""
        production = self._create_production()
        self.assertTrue(production.move_raw_ids, "production should have raw moves")
        self.assertTrue(
            production.move_finished_ids, "production should have finished moves"
        )
        # call directly with no vals (not vals → True) to force the update
        production._update_raw_move_conv_dest_ids()
        for raw_move in production.move_raw_ids:
            self.assertEqual(
                raw_move.move_conv_dest_ids,
                production.move_finished_ids,
                "each raw move must point to all finished moves via move_conv_dest_ids",
            )

    def test_02_conv_orig_ids_inverse_populated(self):
        """Verify finished moves have move_conv_orig_ids pointing back to raw moves."""
        production = self._create_production()
        production._update_raw_move_conv_dest_ids()
        for finished_move in production.move_finished_ids:
            self.assertEqual(
                finished_move.move_conv_orig_ids,
                production.move_raw_ids,
                "each finished move must reference all raw moves via "
                "move_conv_orig_ids",
            )

    def test_03_write_with_move_raw_ids_triggers_conv_link(self):
        """Verify that writing move_raw_ids on production updates conv links."""
        production = self._create_production()
        raw_move = production.move_raw_ids[:1]
        # write move_raw_ids in vals so the write override triggers
        # `_update_raw_move_conv_dest_ids`
        production.write({"move_raw_ids": [Command.link(raw_move.id)]})
        self.assertTrue(
            raw_move.move_conv_dest_ids,
            "raw move must have conv dest links after write that includes move_raw_ids",
        )

    def test_04_finished_picking_empty_without_downstream(self):
        """Verify computed picking fields are empty when no downstream picking
        exists."""
        production = self._create_production()
        self.assertFalse(
            production.finished_picking_ids,
            "finished_picking_ids must be empty when no downstream picking is linked",
        )
        self.assertFalse(
            production.finished_picking_move_ids,
            "finished_picking_move_ids must be empty "
            "when no downstream picking is linked",
        )
        self.assertFalse(
            production.finished_picking_names,
            "finished_picking_names must be empty when no downstream picking is linked",
        )

    def test_05_finished_picking_populated_with_downstream(self):
        """Verify computed picking fields include the downstream picking and
        its move."""
        production = self._create_production()
        finished_move = production.move_finished_ids[:1]
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.warehouse.out_type_id.id,
                "location_id": finished_move.location_dest_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        downstream_move = self.env["stock.move"].create(
            {
                "name": "Downstream Delivery Move",
                "product_id": self.product_finished.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product_finished.uom_id.id,
                "picking_id": picking.id,
                "location_id": finished_move.location_dest_id.id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        finished_move.write({"move_dest_ids": [Command.link(downstream_move.id)]})
        # invalidate cache so computed fields are freshly evaluated
        production.invalidate_recordset()
        self.assertIn(
            picking,
            production.finished_picking_ids,
            "downstream picking must appear in finished_picking_ids",
        )
        self.assertIn(
            downstream_move,
            production.finished_picking_move_ids,
            "downstream move must appear in finished_picking_move_ids",
        )
        self.assertIn(
            picking.name,
            production.finished_picking_names,
            "downstream picking name must appear in finished_picking_names",
        )

    def test_06_log_message_strips_default_state_when_view_ref_matches(self):
        """Verify _log_message removes default_state when form_view_ref matches."""
        production = self._create_production()
        move = production.move_raw_ids[:1]
        move_line = self._create_move_line(move)
        ctx = {
            "form_view_ref": "mrp_traceability.stock_move_details_form_view",
            "default_state": "test_state",
        }
        # record is the object whose context _log_message will strip
        record = move.with_context(**ctx)
        captured = {}

        def fake_parent_log(self_ml, rec, mv, tpl, vals):
            """Capture the record context as received by the parent _log_message."""
            captured["context"] = dict(rec.env.context)

        with patch(
            "odoo.addons.stock.models.stock_move_line.StockMoveLine._log_message",
            fake_parent_log,
        ):
            move_line._log_message(record, move, "stock.track_move_template", {})
        self.assertIn(
            "form_view_ref",
            captured.get("context", {}),
            "form_view_ref must be preserved in context",
        )
        self.assertNotIn(
            "default_state",
            captured.get("context", {}),
            "default_state must be stripped when form_view_ref "
            "matches the traceability view",
        )

    def test_07_log_message_preserves_default_state_without_matching_view_ref(self):
        """Verify _log_message does not strip default_state when form_view_ref
        differs."""
        production = self._create_production()
        move = production.move_raw_ids[:1]
        move_line = self._create_move_line(move)
        ctx = {
            "form_view_ref": "stock.view_move_form",
            "default_state": "test_state",
        }
        record = move.with_context(**ctx)
        captured = {}

        def fake_parent_log(self_ml, rec, mv, tpl, vals):
            """Capture the record context as received by the parent _log_message."""
            captured["context"] = dict(rec.env.context)

        with patch(
            "odoo.addons.stock.models.stock_move_line.StockMoveLine._log_message",
            fake_parent_log,
        ):
            move_line._log_message(record, move, "stock.track_move_template", {})
        self.assertIn(
            "default_state",
            captured.get("context", {}),
            "default_state must not be stripped when form_view_ref does not match",
        )
        self.assertEqual(
            captured["context"]["default_state"],
            "test_state",
        )

    def test_08_stock_move_form_view_has_conv_fields(self):
        """Check that the stock.move inherited form view defines conv fields."""
        view = self.env.ref("mrp_traceability.stock_move_form_view")
        arch = etree.fromstring(view.arch_db.encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn(
            "move_conv_dest_ids",
            field_names,
            "move_conv_dest_ids must be present in stock.move form view",
        )
        self.assertIn(
            "move_conv_orig_ids",
            field_names,
            "move_conv_orig_ids must be present in stock.move form view",
        )

    def test_09_mrp_production_form_view_has_conv_fields(self):
        """Check that move_conv_orig_ids and move_conv_dest_ids appear in the
        mrp.production form view."""
        view_info = self.env["mrp.production"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn(
            "move_conv_orig_ids",
            field_names,
            "move_conv_orig_ids must be present in mrp.production form view",
        )
        self.assertIn(
            "move_conv_dest_ids",
            field_names,
            "move_conv_dest_ids must be present in mrp.production form view",
        )
