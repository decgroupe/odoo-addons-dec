# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from .common import TestMrpProjectAutoCommon


class TestMrpProjectAuto(TestMrpProjectAutoCommon):

    def setUp(self):
        super().setUp()

    def test_01_auto_project_from_orm(self):
        prod1_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/12345678",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
            }
        )
        self.assertTrue(prod1_id)
        self.assertTrue(prod1_id.project_id)
        project_id = prod1_id.project_id
        self.assertEqual(project_id.name, "WH/MO/12345678")
        # change project name to avoid retrieving it
        project_id.sudo().name = "WH/MO/XMAS"
        # try overriding project (1/2)
        prod1_id.action_create_project()
        # ensure project is still the same
        self.assertEqual(prod1_id.project_id, project_id)
        # try overriding project (2/2)
        prod1_id.with_context(override_project_id=True).action_create_project()
        self.assertTrue(prod1_id.project_id)
        # ensure projects are differents
        self.assertNotEqual(prod1_id.project_id, project_id)
        # create a new MO named like existing project
        prod2_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/XMAS",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
            }
        )
        self.assertTrue(prod2_id)
        self.assertTrue(prod2_id.project_id)
        # ensure picked project is the same
        self.assertEqual(prod2_id.project_id, project_id)
        # create a new MO linked manually to an existing project
        prod3_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/SUMMER",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
                "project_id": project_id.id,
            }
        )
        self.assertTrue(prod3_id)
        self.assertTrue(prod3_id.project_id)
        self.assertEqual(prod3_id.project_id, project_id)

    def test_02_auto_project_from_form(self):
        production_id = self._generate_mo(self.product1, self.product1.bom_ids)
        self.assertTrue(production_id)
        self.assertTrue(production_id.project_id)
        self.assertEqual(production_id.project_id.name, "/")

    def test_03_auto_project_disabled(self):
        production_id = (
            self.production_model.with_user(self.production_user)
            .with_context(mrp_project_auto_disable=True)
            .create(
                {
                    "name": "WH/MO/12345678",
                    "product_id": self.product1.id,
                    "product_uom_id": self.product1.uom_id.id,
                }
            )
        )
        self.assertTrue(production_id)
        self.assertFalse(production_id.project_id)

    def test_04_auto_project_using_sale_order(self):
        # WH/MO/00001
        production_id = self.env.ref("mrp.mrp_production_1")
        # S00007
        sale_order_id = self.env.ref("sale.sale_order_7")
        # Link sale order to manufacturing order (not true but for testing only)
        production_id.sale_order_id = sale_order_id
        self.assertFalse(production_id.project_id)
        production_id.action_create_project()
        self.assertTrue(production_id.project_id)
        self.assertEqual(production_id.project_id.name, sale_order_id.name)
