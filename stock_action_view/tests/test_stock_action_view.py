# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2024

from odoo.tests import new_test_user
from odoo.tests.common import SavepointCase


class TestStockActionView(SavepointCase):
    """ """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_procurement_group = cls.env["procurement.group"]
        cls.model_stock_move = cls.env["stock.move"]
        cls.model_stock_picking = cls.env["stock.picking"]
        cls.model_stock_rule = cls.env["stock.rule"]
        cls.model_stock_warehouse_orderpoint = cls.env["stock.warehouse.orderpoint"]
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

    def test_01_procurement_group_action_view(self):
        self._test_action_view_sm_records(self.model_procurement_group)

    def test_02_stock_move_action_view(self):
        self._test_action_view_sm_records(self.model_stock_move)

    def test_03_stock_picking_action_view(self):
        self._test_action_view_sm_records(self.model_stock_picking)

    def test_04_stock_rule_action_view(self):
        self._test_action_view_sm_records(self.model_stock_rule)

    def test_05_stock_warehouse_orderpoint_action_view(self):
        self._test_action_view_sm_records(self.model_stock_warehouse_orderpoint)
