# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026


from odoo import Command
from odoo.tests import Form, new_test_user
from odoo.tests.common import TransactionCase, tagged


# Run tests in post-install because BaseCommon creates a test `res.partner`.
# And there is an issue creating a new partner with required field `autopost_bills`
# in addon account (default value not set up because this addon doesn't depend
# on account)
@tagged("post_install", "-at_install")
class TestProductPricelistAnalysis(TransactionCase):
    """Test Product Pricelist Analysis action view"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ProductTemplate = cls.env["product.template"]
        cls.ProductProduct = cls.env["product.product"]
        cls.ProductPricelist = cls.env["product.pricelist"]
        cls.ProductPricelistItem = cls.env["product.pricelist.item"]
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user = new_test_user(
            cls.env,
            login="action_view-user",
            groups="base.group_user",
            context=ctx,
        )

    def setUp(self):
        super().setUp()
        # default company pricelist is created when "group_product_pricelist" is enabled
        # or when a new company is created, `_activate_or_create_pricelists` is called
        # in both cases. So we can be sure to have a default pricelist for our tests.
        self.env["res.config.settings"].create(
            {"group_product_pricelist": True}
        ).execute()

        self.default_pricelist = self.env["product.pricelist"].search([], limit=1)
        self.assertTrue(self.default_pricelist, "No pricelist found")

        # create some products (as template)
        self.ptA = self.ProductTemplate.create(
            {"name": "Product Template A"},
        )
        self.ptB = self.ProductTemplate.create(
            {"name": "Product Template B"},
        )
        # create some products (as variant)
        self.pC = self.ProductProduct.create(
            {"name": "Product C"},
        )
        self.pD = self.ProductProduct.create(
            {"name": "Product D"},
        )

        # create some pricelist items
        self.pricelist_item_1 = self.ProductPricelistItem.create(
            {
                "pricelist_id": self.default_pricelist.id,
                "product_tmpl_id": self.ptA.id,
                "compute_price": "fixed",
                "fixed_price": 100.0,
            }
        )
        self.pricelist_item_2 = self.ProductPricelistItem.create(
            {
                "pricelist_id": self.default_pricelist.id,
                "product_tmpl_id": self.ptB.id,
                "compute_price": "fixed",
                "fixed_price": 200.0,
            }
        )
        self.pricelist_item_3 = self.ProductPricelistItem.create(
            {
                "pricelist_id": self.default_pricelist.id,
                "product_id": self.pC.id,
                "compute_price": "fixed",
                "fixed_price": 300.0,
            }
        )
        self.pricelist_item_4 = self.ProductPricelistItem.create(
            {
                "pricelist_id": self.default_pricelist.id,
                "product_id": self.pD.id,
                "compute_price": "fixed",
                "fixed_price": 400.0,
            }
        )
        self.product_template_ids = (
            self.ptA | self.ptB | self.pC.product_tmpl_id | self.pD.product_tmpl_id
        )
        self.product_ids = (
            self.pC
            | self.pD
            | self.ptA.product_variant_ids
            | self.ptB.product_variant_ids
        )

    def _test_action_view(self, res_ids, res_model, action_name):
        # user should be allowed to get this action
        action = getattr(res_ids.with_user(self.user), action_name)()
        self.assertEqual(action["res_model"], res_model)
        self.assertEqual(action["type"], "ir.actions.act_window")
        return action

    def _test_action_view_sm_records(
        self, res_ids, action_name="action_view", action_res_model=None
    ):
        """Test for single or multiple records"""
        if action_res_model is None:
            action_res_model = res_ids._name
        self.assertGreaterEqual(len(res_ids), 2)
        # check action for a single record
        action_single = self._test_action_view(
            res_ids[0], action_res_model, action_name
        )
        self.assertIn("form", action_single["view_mode"])
        self.assertIn("res_id", action_single)
        # check action for multiple records
        action_multiple = self._test_action_view(res_ids, action_res_model, action_name)
        self.assertIn("list", action_multiple["view_mode"])
        self.assertIn("domain", action_multiple)
        self.assertIn("views", action_multiple)
        return action_single, action_multiple

    def test_01_product_template_action_view_pricelist_items(self):
        # test that calling `open_pricelist_rules` on multiple records raises
        ERROR_MSG = "Expected singleton"
        with self.assertRaisesRegex(ValueError, ERROR_MSG), self.cr.savepoint():
            action = self.product_template_ids.open_pricelist_rules()
        # test action view for single a records
        action = self.ptA.open_pricelist_rules()
        self.assertEqual(action["res_model"], "product.pricelist.item")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertIn("form", action["view_mode"])
        self.assertIn("res_id", action)
        # no resource directly assigned, res_id should be 0
        self.assertEqual(action["res_id"], 0)
        # data is got from context
        self.assertIn("context", action)
        self.assertEqual(action["context"]["default_applied_on"], "1_product")
        self.assertEqual(
            action["context"]["search_default_product_tmpl_id"],
            self.ptA.id,
        )

    def test_02_product_product_action_view_pricelist_items(self):
        # test that calling `open_pricelist_rules` on multiple records raises
        ERROR_MSG = "Expected singleton"
        with self.assertRaisesRegex(ValueError, ERROR_MSG), self.cr.savepoint():
            action = self.product_ids.open_pricelist_rules()
        # test action view for single a records
        action = self.pC.open_pricelist_rules()
        self.assertEqual(action["res_model"], "product.pricelist.item")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertIn("form", action["view_mode"])
        self.assertIn("res_id", action)
        # no resource directly assigned, res_id should be 0
        self.assertEqual(action["res_id"], 0)
        # data is got from context
        self.assertIn("context", action)
        self.assertEqual(action["context"]["default_applied_on"], "0_product_variant")
        self.assertEqual(
            action["context"]["search_default_product_tmpl_id"],
            self.pC.product_tmpl_id.id,
        )

    # this test is in our PR: https://github.com/odoo/odoo/pull/245444
    def test_pricelist_applied_on_product_variant(self):
        # product template with two variants
        acoustic_bloc_screens = self.env.ref(
            "product.product_template_acoustic_bloc_screens"
        )
        acoustic_bloc_screens_v1 = acoustic_bloc_screens.product_variant_ids[0]
        # create pricelist with rule on template
        pricelist = self.env["product.pricelist"].create(
            {
                "name": "Pricelist for Acoustic Bloc Screens",
                "item_ids": [
                    Command.create(
                        {
                            "compute_price": "fixed",
                            "fixed_price": 123,
                            "base": "list_price",
                            "applied_on": "1_product",
                            "product_tmpl_id": acoustic_bloc_screens.id,
                        }
                    ),
                ],
            }
        )
        # open rule form and change rule to apply on variant instead of template
        with Form(pricelist.item_ids) as item_form:
            item_form.product_id = acoustic_bloc_screens_v1
        # check that `applied_on` changed to variant
        self.assertEqual(pricelist.item_ids.applied_on, "0_product_variant")
        # re-edit rule to apply on template again by clearing `product_id`
        with Form(pricelist.item_ids) as item_form:
            item_form.product_id = self.env["product.product"]
        # check that `applied_on` changed to template
        self.assertEqual(pricelist.item_ids.applied_on, "1_product")
        # check that product_id is cleared
        self.assertFalse(pricelist.item_ids.product_id)
