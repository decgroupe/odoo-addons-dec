# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

from odoo.tests.common import TransactionCase, Form


class TestSaleSoftwareLicensePass(TransactionCase):

    def _send_pass(self, pass_id):
        action = pass_id.action_send()
        wizard = (
            self.env[action["res_model"]].with_context(action["context"]).create({})
        )
        wizard.action_send_mail()

    def setUp(self):
        super().setUp()
        self.product_premium_pass = self.env.ref(
            "sale_software_license_pass.product_premium_pass"
        )
        self.premiumpass_so = self.env.ref("sale_software_license_pass.premiumpass_so")
        self.premiumpass_so_line1 = self.env.ref(
            "sale_software_license_pass.premiumpass_so_line1"
        )
        self.product_freemium_pass = self.env.ref(
            "sale_software_license_pass.product_freemium_pass"
        )
        self.freemiumpass_so = self.env.ref(
            "sale_software_license_pass.freemiumpass_so"
        )
        self.freemiumpass_so_line1 = self.env.ref(
            "sale_software_license_pass.freemiumpass_so_line1"
        )

    def test_01_action_confirm_multiple(self):
        self.assertEqual(len(self.premiumpass_so.license_pass_ids), 1)
        self.premiumpass_so.action_confirm()
        self.assertEqual(len(self.premiumpass_so.license_pass_ids), 1)
        self.premiumpass_so.with_context(
            force_create_application_pass=True
        ).action_confirm()
        self.assertEqual(len(self.premiumpass_so.license_pass_ids), 2)

    def test_02_cancel_sale_order_with_draft_pass(self):
        self.assertEqual(len(self.premiumpass_so.license_pass_ids), 1)
        pass_id = self.premiumpass_so.license_pass_ids
        self.assertEqual(pass_id.state, "draft")
        previous_activity_ids = pass_id.activity_ids
        previous_message_ids = pass_id.message_ids
        self.premiumpass_so.action_cancel()
        new_message_ids = pass_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 1)
        self.assertIn(
            "Automatic cancellation following cancellation of the sell order",
            new_message_ids.body,
        )
        new_activity_ids = pass_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 0)

    def test_03_cancel_sale_order_with_sent_pass(self):
        self.assertEqual(len(self.premiumpass_so.license_pass_ids), 1)
        self.assertEqual(self.premiumpass_so_line1.qty_delivered, 0)
        pass_id = self.premiumpass_so.license_pass_ids
        self._send_pass(pass_id)
        self.assertEqual(pass_id.state, "sent")
        self.assertEqual(self.premiumpass_so_line1.qty_delivered, 3.0)
        previous_activity_ids = pass_id.activity_ids
        previous_message_ids = pass_id.message_ids
        self.premiumpass_so.action_cancel()
        new_message_ids = pass_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        new_activity_ids = pass_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 1)
        self.assertIn(
            "Exception(s) occurred on the sale order(s)",
            new_activity_ids.note,
        )
        self.assertIn(self.premiumpass_so.display_name, new_activity_ids.note)
        self.assertIn("Manual actions may be needed.", new_activity_ids.note)
        self.assertEqual(self.premiumpass_so_line1.qty_delivered, 3.0)
        pass_id.action_cancel()
        self.assertEqual(self.premiumpass_so_line1.qty_delivered, 0.0)

    def test_04_unset_create_application_pass_from_product_form(self):
        self.assertTrue(self.product_premium_pass.license_pack_id)
        self.assertTrue(self.product_premium_pass.product_tmpl_id.license_pack_id)
        with Form(self.product_premium_pass) as product_form:
            product_form.service_tracking = "no"
        self.assertFalse(self.product_premium_pass.license_pack_id)
        self.assertFalse(self.product_premium_pass.product_tmpl_id.license_pack_id)

    def test_05_unset_create_application_pass_from_product_template_form(self):
        self.assertTrue(self.product_premium_pass.license_pack_id)
        self.assertTrue(self.product_premium_pass.product_tmpl_id.license_pack_id)
        with Form(self.product_premium_pass.product_tmpl_id) as product_tmpl_form:
            product_tmpl_form.service_tracking = "no"
        self.assertFalse(self.product_premium_pass.license_pack_id)
        self.assertFalse(self.product_premium_pass.product_tmpl_id.license_pack_id)

    def test_06_setagain_create_application_pass_from_product_form(self):
        license_pack_id = self.product_premium_pass.license_pack_id
        self.assertTrue(license_pack_id)
        self.assertEqual(self.product_premium_pass.license_pack_id, license_pack_id)
        self.assertEqual(
            self.product_premium_pass.product_tmpl_id.license_pack_id, license_pack_id
        )
        with Form(self.product_premium_pass) as product_form:
            product_form.service_tracking = "create_application_pass"
        self.assertEqual(self.product_premium_pass.license_pack_id, license_pack_id)
        self.assertEqual(
            self.product_premium_pass.product_tmpl_id.license_pack_id, license_pack_id
        )

    def test_07_setagain_create_application_pass_from_product_template_form(self):
        license_pack_id = self.product_premium_pass.license_pack_id
        self.assertTrue(license_pack_id)
        self.assertEqual(self.product_premium_pass.license_pack_id, license_pack_id)
        self.assertEqual(
            self.product_premium_pass.product_tmpl_id.license_pack_id, license_pack_id
        )
        with Form(self.product_premium_pass.product_tmpl_id) as product_tmpl_form:
            product_tmpl_form.service_tracking = "create_application_pass"
        self.assertEqual(self.product_premium_pass.license_pack_id, license_pack_id)
        self.assertEqual(
            self.product_premium_pass.product_tmpl_id.license_pack_id, license_pack_id
        )

    def test_08_unset_license_pack(self):
        self.assertTrue(self.product_premium_pass.product_tmpl_id.license_pack_id)
        self.product_premium_pass.product_tmpl_id.license_pack_id = False
        self.assertFalse(self.product_premium_pass.license_pack_id)
        self.assertFalse(self.product_premium_pass.product_tmpl_id.license_pack_id)

    def test_09_set_pack_from_product(self):
        with Form(self.env["software.license.pass"]) as pass_form:
            pass_form.product_id = self.product_premium_pass
            pass_id = pass_form.save()
        self.assertEqual(pass_id.pack_id, self.product_premium_pass.license_pack_id)

    def test_10_add_pass_to_so(self):
        self.assertEqual(self.premiumpass_so.license_pass_count, 1)
        with Form(self.premiumpass_so) as so_form:
            with so_form.order_line.new() as sol_form:
                sol_form.product_id = self.product_premium_pass
        self.assertEqual(self.premiumpass_so.license_pass_count, 2)

    def test_11_qty_delivered_so(self):
        self.assertEqual(self.freemiumpass_so.license_pass_count, 0)
        self.freemiumpass_so.action_confirm()
        self.assertEqual(self.freemiumpass_so.license_pass_count, 1)
        self.assertEqual(self.freemiumpass_so_line1.qty_delivered, 0)
        pass_id = self.freemiumpass_so.license_pass_ids
        self._send_pass(pass_id)
        self.assertEqual(pass_id.state, "sent")
        self.assertEqual(self.freemiumpass_so_line1.qty_delivered, 2.0)
