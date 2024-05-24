# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2024

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestMrpProductionRequestCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_production_request = cls.env["mrp.production.request"]
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
        # [FURN_7800] Desk Combination
        cls.request1 = cls.env["mrp.production.request"].create(
            {
                "product_id": cls.env.ref("product.product_product_3").id,
                "bom_id": cls.env.ref("mrp.mrp_bom_manufacture").id,
            }
        )
        # [FURN_9666] Table
        cls.request2 = cls.env["mrp.production.request"].create(
            {
                "product_id": cls.env.ref("mrp.product_product_computer_desk").id,
                "bom_id": cls.env.ref("mrp.mrp_bom_desk").id,
            }
        )


class TestMrpProductionRequestActionViewCommon(TestMrpProductionRequestCommon):

    def _test_action_view(self, res_ids, res_model):
        # any base user should be allowed to get this action
        action = res_ids.with_user(self.user).action_view()
        self.assertEqual(action["res_model"], res_model)
        self.assertEqual(action["type"], "ir.actions.act_window")
        return action

    def _test_action_view_sm_records(self, model):
        """Test for single or multiple records"""
        res_ids = model.search([])
        self.assertGreaterEqual(len(res_ids), 2)
        # check action for a single record
        action_single = self._test_action_view(res_ids[0], model._name)
        self.assertIn("form", action_single["view_mode"])
        self.assertIn("res_id", action_single)
        # check action for multiple records
        action_multiple = self._test_action_view(res_ids, model._name)
        self.assertIn("tree", action_multiple["view_mode"])
        self.assertIn("domain", action_multiple)
        self.assertIn("views", action_multiple)
