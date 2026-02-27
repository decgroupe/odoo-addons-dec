# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2026


from odoo.addons.project_identification.tests.common import (
    TestProjectIdentificationBase,
)


class TestProjectPartnerLocation(TestProjectIdentificationBase):
    """Test the `project_partner_location` module."""

    def setUp(self):
        super().setUp()

    def test_01_field_names(self):
        self.assertIn("partner_shipping_id", self.model_project._fields)
        self.assertIn("partner_shipping_zip_id", self.model_project._fields)
        self.assertIn("partner_shipping_country_id", self.model_project._fields)
        self.assertIn("partner_shipping_id", self.model_task._fields)
        self.assertIn("partner_shipping_zip_id", self.model_task._fields)
        self.assertIn("partner_shipping_country_id", self.model_task._fields)

    def test_02_project_partner_shipping_id(self):
        self._create_projects()
        partner_id = self.env["res.partner"].create(
            {
                "name": "Partner A",
                "street": "123 Main St",
                "zip": "12345b Cedex",
                "city": "CityA",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        sale_order_id = self.env["sale.order"].create(
            {
                "name": "SO_TEST_02",
                "partner_id": partner_id.id,
                "partner_shipping_id": partner_id.id,
                "project_id": False,
            }
        )
        self.assertFalse(self.pA.partner_shipping_id)
        self.assertFalse(self.pB.partner_shipping_id)
        # change the project name to match the sale order name to link them
        self.pA.name = "SO_TEST_02"
        self.assertEqual(self.pA.partner_shipping_id, partner_id)
        # change the project name to unlink it from the sale order
        self.pA.name = "ProjectA"
        self.assertFalse(self.pA.partner_shipping_id)
        # manually set the sale order field on project B to link them
        self.pB.sale_order_id = sale_order_id
        self.assertEqual(self.pB.partner_shipping_id, partner_id)
        # unset the sale order field to unlink them
        self.pB.sale_order_id = False
        self.assertFalse(self.pB.partner_shipping_id)
        # set the project field on the sale order to link it to project A
        sale_order_id.project_id = self.pA.id
        self.assertEqual(self.pA.partner_shipping_id, partner_id)
        # unset the project field on the sale order to unlink it from project A
        sale_order_id.project_id = False
        self.assertFalse(self.pA.partner_shipping_id)

    def test_03_task_partner_shipping_id(self):
        self._create_projects()
        self._create_tasks()
        partner_id = self.env["res.partner"].create(
            {
                "name": "Partner A",
                "street": "123 Main St",
                "zip": "12345b Cedex",
                "city": "CityA",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        sale_order_id = self.env["sale.order"].create(
            {
                "name": "SO_TEST_03",
                "partner_id": partner_id.id,
                "partner_shipping_id": partner_id.id,
                "project_id": False,
            }
        )
        product_id = self.env["product.product"].create({"name": "Test Product"})
        production_id = self.env["mrp.production"].create(
            {
                "name": "PROD_TEST_03",
                "partner_id": partner_id.id,
                "product_id": product_id.id,
            }
        )
        self.assertFalse(self.t1.sale_order_id)
        self.assertFalse(self.t1.partner_shipping_id)
        # set the sale order field on task 1 to link it and get the partner from it
        self.t1.sale_order_id = sale_order_id
        self.assertEqual(self.t1.partner_shipping_id, partner_id)
        # unset the sale order field to unlink it lose the reference
        self.t1.sale_order_id = False
        self.assertFalse(self.t1.partner_shipping_id)
        # set the production field on task 1 to link it and get the partner
        self.t1.production_id = production_id
        self.assertEqual(self.t1.partner_shipping_id, partner_id)
        # unset the production field to unlink it and lose the reference
        self.t1.production_id = False
        self.assertFalse(self.t1.partner_shipping_id)
        # assign a shipping partner on project A
        self.assertFalse(self.tA1.partner_shipping_id)
        self.pA.partner_shipping_id = partner_id
        self.assertEqual(self.tA1.partner_shipping_id, partner_id)
        # unassign the partner on project A and check the task lose the reference
        self.pA.partner_shipping_id = False
        self.assertFalse(self.tA1.partner_shipping_id)

    def test_04_project_display_name(self):
        self._create_projects()
        self.assertFalse(self.pA.partner_shipping_id)
        self.assertProjectDisplayName(
            self.pA,
            {"name_search": True},
            "ProjectA",
            "ProjectA",
        )
        # create a new partner and its dedicated delivery address
        partner_id = self.env["res.partner"].create(
            {
                "name": "Partner A",
                "street": "123 Main St",
                "zip": "12345b Cedex",
                "city": "CityA",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        partner_shipping_city_id = self.env["res.city"].create(
            {
                "name": "CityA",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        partner_shipping_zip_id = self.env["res.city.zip"].create(
            {
                "name": "12345",
                "city_id": partner_shipping_city_id.id,
                "country_id": self.env.ref("base.fr").id,
            }
        )
        partner_shipping_id = self.env["res.partner"].create(
            {
                "name": "Delivery Address A",
                "zip_id": partner_shipping_zip_id.id,
                "type": "delivery",
                "parent_id": partner_id.id,
            }
        )
        # create a new sale order with this new partner and its dedicated delivery
        # address and link it to the project
        self.env["sale.order"].create(
            {
                "name": "SO_TEST_03",
                "partner_id": partner_id.id,
                "partner_shipping_id": partner_shipping_id.id,
                "project_id": self.pA.id,
            }
        )
        self.assertEqual(self.pA.partner_shipping_id, partner_shipping_id)
        self.assertEqual(self.pA.partner_shipping_zip_id, partner_shipping_id.zip_id)
        self.assertProjectDisplayName(
            self.pA,
            {"name_search": True},
            "ProjectA",
            "ProjectA 👷 Partner A, Delivery Address A → (🗺️ 12345 CityA, France)",
        )
        # for project B, only assign a partner
        self.assertProjectNameSearchEqual(
            self.pB,
            "ProjectB",
            "ProjectB → ⏱️",
        )
        partner_id = self.env["res.partner"].create(
            {
                "name": "Partner B",
                "street": "234 Main St",
                "zip": "23456",
                "city": "CityB",
                "country_id": self.env.ref("base.fr").id,
            }
        )
        self.pB.partner_id = partner_id
        self.assertEqual(self.pB.partner_id, partner_id)
        self.assertFalse(self.pB.partner_shipping_id)
        self.assertFalse(self.pB.partner_shipping_zip_id)
        self.assertProjectDisplayName(
            self.pB,
            {"name_search": True},
            "ProjectB",
            "ProjectB → ⏱️ 👷 Partner B → (23456 CityB)",
        )
