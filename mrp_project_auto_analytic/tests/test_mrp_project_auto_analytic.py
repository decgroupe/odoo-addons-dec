# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.addons.mrp_project_auto.tests.common import TestMrpProjectAutoCommon


class TestMrpProjectAutoAnalytic(TestMrpProjectAutoCommon):

    def setUp(self):
        super().setUp()

    def test_01_auto_project_parent_analytic_account(self):
        analytic_production = self.env.ref("mrp_project.analytic_production")
        prod1_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/12345678",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
            }
        )
        self.assertTrue(prod1_id.project_id)
        project_id = prod1_id.project_id
        self.assertEqual(project_id.name, "WH/MO/12345678")
        self.assertEqual(project_id.analytic_account_id.parent_id, analytic_production)
