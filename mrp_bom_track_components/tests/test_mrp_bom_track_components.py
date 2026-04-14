# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command

from .common import TestMrpBomTrackComponentsCommon


class TestMrpBomTrackComponents(TestMrpBomTrackComponentsCommon):
    """Tests for mrp_bom_track_components module."""

    def test_01_write_tracks_added_bom_line(self):
        """Check that writing bom_line_ids posts a tracking note for added lines."""
        initial_message_count = len(self.bom.message_ids)
        # add a new component line via write - should trigger tracking
        self.bom.write(
            {
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_comp2.id,
                            "product_qty": 2.0,
                        }
                    ),
                ]
            }
        )
        # a tracking note should have been posted
        self.assertGreater(len(self.bom.message_ids), initial_message_count)

    def test_02_write_tracks_edited_bom_line(self):
        """Check that modifying bom_line_ids posts a tracking note for edited lines."""
        bom_line = self.bom.bom_line_ids[0]
        initial_message_count = len(self.bom.message_ids)
        # change the product of the existing line via write
        self.bom.write(
            {
                "bom_line_ids": [
                    Command.update(
                        bom_line.id,
                        {"product_id": self.product_comp2.id},
                    ),
                ]
            }
        )
        self.assertGreater(len(self.bom.message_ids), initial_message_count)

    def test_03_write_tracks_removed_bom_line(self):
        """Check that removing a bom line via write posts a tracking note."""
        bom_line = self.bom.bom_line_ids[0]
        initial_message_count = len(self.bom.message_ids)
        # delete the existing line via write
        self.bom.write(
            {
                "bom_line_ids": [
                    Command.delete(bom_line.id),
                ]
            }
        )
        self.assertGreater(len(self.bom.message_ids), initial_message_count)

    def test_04_get_track_state_snapshot(self):
        """Check that get_track_state returns a snapshot of tracked field values."""
        state = self.bom.get_track_state()
        bom_line_id = str(self.bom.bom_line_ids[0].id)
        self.assertIn(bom_line_id, state)
        self.assertIn("product_id", state[bom_line_id])
        self.assertIn("product_qty", state[bom_line_id])

    def test_05_write_tracks_qty_change(self):
        """Check that writing a float field on a bom line posts a tracking note."""
        bom_line = self.bom.bom_line_ids[0]
        initial_message_count = len(self.bom.message_ids)
        # change product_qty (a float field) via write on the bom
        self.bom.write(
            {
                "bom_line_ids": [
                    Command.update(bom_line.id, {"product_qty": 5.0}),
                ]
            }
        )
        self.assertGreater(len(self.bom.message_ids), initial_message_count)
