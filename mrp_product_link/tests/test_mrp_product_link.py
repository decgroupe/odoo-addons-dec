# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from datetime import timedelta

from odoo import Command, fields
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestMrpProductLink(TransactionCase):
    """Tests for mrp_product_link module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Finished Product",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.component = cls.env["product.product"].create(
            {
                "name": "Test Component",
                "type": "consu",
                "is_storable": True,
            }
        )
        cls.bom = cls.env["mrp.bom"].create(
            {
                "product_id": cls.product.id,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
                "product_uom_id": cls.uom_unit.id,
                "product_qty": 1.0,
                "type": "normal",
                "bom_line_ids": [
                    Command.create({"product_id": cls.component.id, "product_qty": 1.0})
                ],
            }
        )

    def _create_mo(self, qty=1.0, confirm=True):
        """Create and optionally confirm a manufacturing order for cls.product."""
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = self.product
        mo_form.bom_id = self.bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        if confirm:
            mo.action_confirm()
        return mo

    def test_01_mrp_product_qty_counts_confirmed_mo(self):
        """Confirmed (not done) MOs are included in mrp_product_qty."""
        self.product.invalidate_recordset()
        qty_before = self.product.mrp_product_qty
        mo = self._create_mo(qty=3.0)
        self.assertEqual(mo.state, "confirmed")
        self.product.invalidate_recordset()
        qty_after = self.product.mrp_product_qty
        self.assertEqual(qty_after - qty_before, 3.0)

    def test_02_mrp_product_qty_counts_old_mo(self):
        """MOs older than 365 days are still included in mrp_product_qty."""
        mo = self._create_mo(qty=5.0)
        # force date_start to more than 1 year ago
        old_date = fields.Datetime.now() - timedelta(days=400)
        mo.write({"date_start": old_date})
        self.product.invalidate_recordset()
        qty = self.product.mrp_product_qty
        self.assertGreaterEqual(qty, 5.0)

    def test_03_action_view_mos_product_no_state_filter(self):
        """action_view_mos on product.product must not filter by state=done."""
        action = self.product.action_view_mos()
        domain = action.get("domain", [])
        for leaf in domain:
            if isinstance(leaf, list | tuple) and len(leaf) == 3:
                field, _op, value = leaf
                self.assertFalse(
                    field == "state" and value == "done",
                    "domain must not contain ('state', '=', 'done')",
                )
        # the product_id filter must be present
        product_ids_in_domain = [
            leaf[2]
            for leaf in domain
            if isinstance(leaf, list | tuple)
            and len(leaf) == 3
            and leaf[0] == "product_id"
        ]
        self.assertTrue(product_ids_in_domain, "domain must filter by product_id")
        self.assertIn(self.product.id, product_ids_in_domain[0])

    def test_04_action_view_mos_template_no_state_filter(self):
        """action_view_mos on product.template must not filter by state=done."""
        tmpl = self.product.product_tmpl_id
        action = tmpl.action_view_mos()
        domain = action.get("domain", [])
        for leaf in domain:
            if isinstance(leaf, list | tuple) and len(leaf) == 3:
                field, _op, value = leaf
                self.assertFalse(
                    field == "state" and value == "done",
                    "domain must not contain ('state', '=', 'done')",
                )
        # search_default_filter_plan_date must be disabled (0)
        context = action.get("context", {})
        self.assertEqual(
            context.get("search_default_filter_plan_date"),
            0,
            "search_default_filter_plan_date must be 0",
        )
