# Copyright 2018 Eficent Business and IT Consulting Services S.L.
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests import Form
from .common import TestMrpPurchaseCommon


class TestMrpPurchase(TestMrpPurchaseCommon):

    def setUp(self):
        super(TestMrpPurchase, self).setUp()
        # Create bom lines
        self.bom_line_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": self.service.id,
                "product_qty": 2,
            }
        )

    def _generate_mo(self, product, bom, qty=1.0):
        mo_form = Form(self.env["mrp.production"])
        mo_form.product_id = product
        mo_form.bom_id = bom
        mo_form.product_qty = qty
        mo = mo_form.save()
        return mo

    def test_01_create_service(self):
        """Explode bill of material and look for a production service."""
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.action_confirm()
        # check created purchase order line
        po_lines = self.env["purchase.order.line"].search(
            [("product_id", "in", self.bom.bom_line_ids.mapped("product_id.id"))]
        )
        self.assertEqual(len(po_lines), 1)
        self.assertEqual(po_lines.product_id.type, "service")
        self.assertEqual(po_lines.product_qty, 6.0)
        # check related/computed data
        self.assertEqual(production_id.purchase_line_ids, po_lines)
        self.assertEqual(po_lines.production_ids, production_id)
        self.assertEqual(po_lines.production_id, production_id)

    def test_02_service_not_purchasable(self):
        self.service.purchase_ok = False
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        # store current chat/activity data for future uses
        previous_activity_ids = production_id.activity_ids
        previous_message_ids = production_id.message_ids
        production_id.action_confirm()
        # a warning message should be posted
        new_message_ids = production_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 1)
        self.assertIn(
            "The procurement workflow for this line is not supported",
            new_message_ids.body,
        )
        # no activities should be created
        new_activity_ids = production_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 0)

    def test_03_cancel_purchase_order_without_notification(self):
        self.service.purchase_ok = False
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        # store current chat/activity data for future uses
        previous_activity_ids = production_id.activity_ids
        previous_message_ids = production_id.message_ids
        production_id.with_context(procurement_fail_no_notify=True).action_confirm()
        # no warning message should be posted
        new_message_ids = production_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        # no activities should be created
        new_activity_ids = production_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 0)

    def test_04_cancel_purchase_order(self):
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.action_confirm()
        # store current chat/activity data for future uses
        previous_activity_ids = production_id.activity_ids
        previous_message_ids = production_id.message_ids
        # cancel purchase order
        purchase_order_id = production_id.purchase_line_ids.order_id
        purchase_order_id.button_cancel()
        # no warning message should be posted
        new_message_ids = production_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        # a new activity should be created
        new_activity_ids = production_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 1)
        self.assertIn(
            "Exception(s) occurred on the purchase order(s)",
            new_activity_ids.note,
        )

    def test_05_cancel_production_order(self):
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.action_confirm()
        purchase_order_id = production_id.purchase_line_ids.order_id
        # store current chat/activity data for future uses
        previous_activity_ids = purchase_order_id.activity_ids
        previous_message_ids = purchase_order_id.message_ids
        # cancel production order
        production_id.action_cancel()
        # no warning message should be posted
        new_message_ids = purchase_order_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        # a new activity should be created
        new_activity_ids = purchase_order_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 1)
        self.assertIn(
            "Exception(s) occurred on the production order(s)",
            new_activity_ids.note,
        )
