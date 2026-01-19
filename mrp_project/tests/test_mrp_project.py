# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026

from odoo.tests.common import TransactionCase


class TestMrpProject(TransactionCase):
    def setUp(self):
        super().setUp()
        self.Project = self.env["project.project"]
        self.Production = self.env["mrp.production"]

    def test_01_project_production_link(self):
        project = self.Project.create({"name": "Test Project"})
        self.assertEqual(project.production_count, 0)
        self.assertEqual(project.todo_production_count, 0)
        ### create two manufacturing orders linked to this project
        # first MO
        production1 = self.Production.create(
            {
                "name": "Production 1",
                "product_id": self.env.ref(
                    "mrp.product_product_computer_desk_screw"
                ).id,
                "product_qty": 10,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "project_id": project.id,
            }
        )
        self.assertEqual(production1.state, "draft")
        # check action view
        action = project.action_view_productions()
        self.assertEqual(action["res_id"], production1.id)
        # create second MO
        production2 = self.Production.create(
            {
                "name": "Production 2",
                "product_id": self.env.ref("mrp.product_product_computer_desk_bolt").id,
                "product_qty": 5,
                "product_uom_id": self.env.ref("uom.product_uom_unit").id,
                "project_id": project.id,
            }
        )
        self.assertEqual(production2.state, "draft")
        # check counts
        self.assertEqual(project.production_count, 2)
        self.assertEqual(project.todo_production_count, 2)
        # check action view
        action = project.action_view_productions()
        self.assertEqual(
            action["domain"], [("id", "in", [production1.id, production2.id])]
        )
        # confirm one MO
        production1.action_confirm()
        self.assertEqual(production1.state, "confirmed")
        # check counts again
        self.assertEqual(project.production_count, 2)
        self.assertEqual(project.todo_production_count, 2)
        # mark one MO as done
        production1.button_mark_done()
        self.assertEqual(production1.state, "done")
        # check counts again
        self.assertEqual(project.production_count, 2)
        self.assertEqual(project.todo_production_count, 1)
