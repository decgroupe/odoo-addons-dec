# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo import Command

from odoo.addons.queue_job.tests.common import trap_jobs

from .common import TestMrpBomReplaceComponentsCommon


class TestMrpBomReplaceComponents(TestMrpBomReplaceComponentsCommon):
    """Tests for mrp_bom_replace_components module."""

    def _make_wizard(self, boms):
        """Create and return a replace.bom.components wizard for the given BoMs."""
        ctx = {
            "active_model": "mrp.bom",
            "active_ids": boms.ids,
        }
        wizard = (
            self.env["replace.bom.components"]
            .with_context(**ctx)
            .create(
                self.env["replace.bom.components"]
                .with_context(**ctx)
                .default_get(["bom_ids", "bom_product_ids", "replacement_ids"])
            )
        )
        return wizard

    def test_01_default_get_populates_bom_fields(self):
        """Check that default_get fills bom_ids and bom_product_ids from context."""
        ctx = {
            "active_model": "mrp.bom",
            "active_ids": self.bom.ids,
        }
        rec = (
            self.env["replace.bom.components"]
            .with_context(**ctx)
            .default_get(["bom_ids", "bom_product_ids"])
        )
        self.assertIn(self.bom.id, rec.get("bom_ids", []))
        self.assertIn(self.product_old.id, rec.get("bom_product_ids", []))

    def test_02_default_get_ignores_non_bom_model(self):
        """Check that default_get ignores context when active_model is not mrp.bom."""
        ctx = {
            "active_model": "product.product",
            "active_ids": [self.product_old.id],
        }
        rec = (
            self.env["replace.bom.components"]
            .with_context(**ctx)
            .default_get(["bom_ids", "bom_product_ids"])
        )
        self.assertFalse(rec.get("bom_ids"))
        self.assertFalse(rec.get("bom_product_ids"))

    def test_03_do_replace_changes_component(self):
        """Check that _do_replace replaces the old product with the new one in BoM."""
        wizard = self._make_wizard(self.bom)
        wizard.write(
            {
                "replacement_ids": [
                    Command.create(
                        {
                            "previous_product_id": self.product_old.id,
                            "new_product_id": self.product_new.id,
                        }
                    ),
                ]
            }
        )
        wizard._do_replace()
        bom_line_product_ids = self.bom.bom_line_ids.mapped("product_id")
        self.assertIn(self.product_new, bom_line_product_ids)
        self.assertNotIn(self.product_old, bom_line_product_ids)

    def test_04_do_replace_only_targets_selected_boms(self):
        """Check that _do_replace only replaces in the BoMs listed in bom_ids."""
        other_bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_finished.product_tmpl_id.id,
                "bom_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_old.id,
                            "product_qty": 2.0,
                        }
                    ),
                ],
            }
        )
        # wizard only targets self.bom, not other_bom
        wizard = self._make_wizard(self.bom)
        wizard.write(
            {
                "replacement_ids": [
                    Command.create(
                        {
                            "previous_product_id": self.product_old.id,
                            "new_product_id": self.product_new.id,
                        }
                    ),
                ]
            }
        )
        wizard._do_replace()
        # self.bom should have the new component
        self.assertIn(self.product_new, self.bom.bom_line_ids.mapped("product_id"))
        # other_bom should be unchanged
        self.assertIn(self.product_old, other_bom.bom_line_ids.mapped("product_id"))

    def test_05_action_replace_enqueues_job(self):
        """Check that action_replace enqueues a delayed job instead of
        running inline."""
        wizard = self._make_wizard(self.bom)
        wizard.write(
            {
                "replacement_ids": [
                    Command.create(
                        {
                            "previous_product_id": self.product_old.id,
                            "new_product_id": self.product_new.id,
                        }
                    ),
                ]
            }
        )
        with trap_jobs() as trap:
            wizard.action_replace()
            trap.assert_jobs_count(1)
            trap.assert_enqueued_job(
                wizard._do_replace,
                args=(),
                kwargs={},
            )
