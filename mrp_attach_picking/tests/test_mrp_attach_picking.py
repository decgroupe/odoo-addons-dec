# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2023

from odoo.addons.mrp.tests.common import TestMrpCommon
from odoo.exceptions import ValidationError
from odoo.tests import Form


class TestMrpAttachPicking(TestMrpCommon):
    def setUp(self):
        super().setUp()
        self.attach_picking_wizard_model = self.env["mrp.attach.picking"]
        self.production = self.env.ref("mrp.mrp_production_3")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.partner = self.env["res.partner"].create({"name": "MyPartner"})

    def _create_customer_move(self, product, qty):
        location_src_id = self.stock_location
        location_dest_id = self.customer_location
        picking_out = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "location_id": location_src_id.id,
                "location_dest_id": location_dest_id.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
            }
        )
        customer_move = self._create_move(
            product=product,
            src_location=location_src_id,
            dst_location=location_dest_id,
            product_uom_qty=qty,
            picking_id=picking_out.id,
        )
        return picking_out, customer_move

    def _find_waiting_picking_move(self, product, qty):
        """Use the same domain that the one set in the wizard view"""
        domain = [
            ("product_id", "=", product.id),
            ("product_uom_qty", "=", qty),
            ("move_orig_ids", "=", False),
            ("procure_method", "=", "make_to_stock"),
            ("state", "in", ("assigned", "confirmed")),
            ("location_dest_id.usage", "=", "customer"),
        ]
        return self.env["stock.move"].search(domain)

    def _run_common_test(
        self, opt_confirm_mo=True, opt_done_mo=False, opt_find_move=True
    ):
        new_production = self.production.copy()
        if opt_confirm_mo:
            new_production.action_confirm()
        if opt_done_mo:
            np = Form(new_production)
            np.qty_producing = np.product_qty
            np.save()
            new_production.action_generate_serial()
            new_production.button_mark_done()
        self.assertTrue(new_production.allow_attach_picking)
        # create picking out
        picking_out, customer_move = self._create_customer_move(
            new_production.product_id, new_production.product_uom_qty
        )
        picking_out.action_confirm()
        self.assertEqual(customer_move.state, "confirmed")
        self.assertEqual(customer_move.procure_method, "make_to_stock")
        # find move
        if opt_find_move:
            move_ids = self._find_waiting_picking_move(
                new_production.product_id, new_production.product_uom_qty
            )
            self.assertTrue(move_ids)
        else:
            move_ids = self.env["stock.move"]
        # attach using wizard
        ctx = {
            "active_model": new_production._name,
            "active_id": new_production.id,
        }
        wizard_form = Form(self.attach_picking_wizard_model.with_context(ctx))
        wizard_form.move_id = move_ids and move_ids[0]
        wizard_id = wizard_form.save()
        wizard_id.do_attach()
        # check attach
        if opt_done_mo:
            self.assertEqual(customer_move.state, "assigned")
        else:
            self.assertEqual(customer_move.state, "waiting")
        self.assertEqual(customer_move.procure_method, "make_to_order")
        self.assertFalse(new_production.allow_attach_picking)
        self.assertEqual(new_production.move_finished_ids, customer_move.move_orig_ids)
        self.assertEqual(new_production.move_finished_ids.move_dest_ids, customer_move)

    def test_01_attach_without_move(self):
        with self.assertRaisesRegex(
            AssertionError, "move_id is a required field"
        ), self.cr.savepoint():
            self._run_common_test(opt_find_move=False)

    def test_02_attach_draft_mo(self):
        with self.assertRaisesRegex(
            ValidationError, "None of the production finished moves can be linked"
        ), self.cr.savepoint():
            self._run_common_test(opt_confirm_mo=False)

    def test_03_attach(self):
        self._run_common_test()

    def test_04_attach_done_mo(self):
        self._run_common_test(opt_done_mo=True)
