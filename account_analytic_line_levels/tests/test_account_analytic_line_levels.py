# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.tests import common


class TestAccountAnalyticLineLevels(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.analytic_account_model = self.env["account.analytic.account"]
        self.analytic_line_model = self.env["account.analytic.line"]
        self.line_integration_task = self.env.ref("account_analytic_line_levels.aal_it")
        self.line_online_publish = self.env.ref("account_analytic_line_levels.aal_op")

        self.account_al0 = self.analytic_account_model.create(
            {
                "name": "Account A (level0)",
            }
        )
        self.account_al1 = self.analytic_account_model.create(
            {
                "name": "Account A (level1)",
                "parent_id": self.account_al0.id,
            }
        )
        self.account_al2 = self.analytic_account_model.create(
            {
                "name": "Account A (level2)",
                "parent_id": self.account_al1.id,
            }
        )
        self.account_al3 = self.analytic_account_model.create(
            {
                "name": "Account A (level3)",
                "parent_id": self.account_al2.id,
            }
        )

        self.line_accounta_task = self.analytic_line_model.create(
            {
                "account_id": self.account_al1.id,
                "name": "Task in group A",
                "date": (datetime.now() + relativedelta(weekday=6, weeks=-1)).strftime(
                    "%Y-%m-%d"
                ),
                "amount": 4,
                "unit_amount": 1.0,
            }
        )

    def test_01_two_levels(self):
        self.assertEqual(
            self.line_integration_task.account_primary_id,
            self.env.ref("analytic.analytic_our_super_product"),
        )
        self.assertEqual(
            self.line_integration_task.account_secondary_id,
            self.env.ref("account_analytic_parent.analytic_integration"),
        )
        self.assertFalse(
            self.line_integration_task.account_tertiary_id,
        )

    def test_02_three_levels(self):
        self.assertEqual(
            self.line_online_publish.account_primary_id,
            self.env.ref("analytic.analytic_internal"),
        )
        self.assertEqual(
            self.line_online_publish.account_secondary_id,
            self.env.ref("account_analytic_parent.analytic_journal_trainings"),
        )
        self.assertEqual(
            self.line_online_publish.account_tertiary_id,
            self.env.ref("account_analytic_parent.analytic_online"),
        )

    def test_03_levels_computation(self):
        self.assertEqual(
            self.line_accounta_task.account_primary_id,
            self.account_al0,
        )
        self.assertEqual(
            self.line_accounta_task.account_secondary_id,
            self.account_al1,
        )
        self.assertFalse(
            self.line_accounta_task.account_tertiary_id,
        )
