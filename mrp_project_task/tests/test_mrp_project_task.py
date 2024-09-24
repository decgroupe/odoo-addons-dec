# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

from odoo.tests.common import TransactionCase
from odoo.addons.mrp_purchase.tests.common import TestMrpPurchaseCommon


class TestMrpProjectTask(TestMrpPurchaseCommon):

    def setUp(self):
        super().setUp()
        self.product_uom_hour = self.env.ref("uom.product_uom_hour")
        self.product_uom_day = self.env.ref("uom.product_uom_day")
        self.service_in_project = self.product_model.create(
            {
                "name": "Internal Check-Service",
                "type": "service",
                "service_tracking": "task_in_project",
            }
        )
        self.service_in_project_no_tracking = self.product_model.create(
            {
                "name": "Internal Check-Service",
                "type": "service",
                "service_tracking": "no",
            }
        )
        self.service_in_project_hours = self.product_model.create(
            {
                "name": "Internal Check-Service",
                "type": "service",
                "service_tracking": "task_in_project",
                "uom_id": self.product_uom_hour.id,
                "uom_po_id": self.product_uom_hour.id,
            }
        )
        self.service_in_project_days = self.product_model.create(
            {
                "name": "Internal Check-Service",
                "type": "service",
                "service_tracking": "task_in_project",
                "uom_id": self.product_uom_day.id,
                "uom_po_id": self.product_uom_day.id,
            }
        )
        self.project_id = (
            self.env["project.project"]
            .sudo()
            .create({"name": "TestMrpProjectTask-Project"})
        )

    def _add_bom_line(self, product_id):
        # add a new bom line
        return self.bom_line_model.create(
            {
                "bom_id": self.bom.id,
                "product_id": product_id.id,
                "product_qty": 1,
            }
        )

    def test_01_no_tracking_set(self):
        bom_line_id = self._add_bom_line(self.service_in_project_no_tracking)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        # service is incorrectly set, so no task created
        self.assertFalse(production_id.task_ids)
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)

    def test_02_wrong_unit_category(self):
        bom_line_id = self._add_bom_line(self.service_in_project)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.name = "MO/TEST/02"
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        self.assertEqual(production_id.task_count, 1)
        self.assertEqual(production_id.task_progress, 0)
        task_id = production_id.task_ids
        # as fallback, we consider quantities are hours
        self.assertEqual(task_id.planned_hours, 1.0)
        # naming check
        name_identifications = production_id.task_ids._get_name_identifications()
        self.assertIn("🔧 MO/TEST/02", name_identifications)

    def test_03_same_unit_category_as_company(self):
        bom_line_id = self._add_bom_line(self.service_in_project_days)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.name = "MO/TEST/03"
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        self.assertEqual(production_id.task_count, 1)
        self.assertEqual(production_id.task_progress, 0)
        task_id = production_id.task_ids
        # quantities were converted from days to hours
        self.assertEqual(task_id.planned_hours, 8.0)
        # naming check
        name_identifications = production_id.task_ids._get_name_identifications()
        self.assertIn("🔧 MO/TEST/03", name_identifications)

    def test_04_unknown_reference_unit(self):
        categ_unit = self.env["uom.category"].create(
            {
                "name": "Bloggish",
            }
        )
        self.env.user.company_id.project_time_mode_id = self.env["uom.uom"].create(
            {
                "name": "Parsec",
                "category_id": categ_unit.id,
            }
        )
        bom_line_id = self._add_bom_line(self.service_in_project_days)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.name = "MO/TEST/04"
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        self.assertEqual(production_id.task_count, 1)
        self.assertEqual(production_id.task_progress, 0)
        task_id = production_id.task_ids
        # quantities were converted from days to hours
        self.assertEqual(task_id.planned_hours, 8.0)
        # naming check
        name_identifications = production_id.task_ids._get_name_identifications()
        self.assertIn("🔧 MO/TEST/04", name_identifications)

    def test_05_same_unit_as_company(self):
        bom_line_id = self._add_bom_line(self.service_in_project_hours)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.name = "MO/TEST/05"
        self.assertEqual(production_id.task_count, 0)
        self.assertEqual(production_id.task_progress, 100)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        self.assertEqual(production_id.task_count, 1)
        self.assertEqual(production_id.task_progress, 0)
        task_id = production_id.task_ids
        # quantities are hours
        self.assertEqual(task_id.planned_hours, 1.0)
        # naming check
        name_identifications = production_id.task_ids._get_name_identifications()
        self.assertIn("🔧 MO/TEST/05", name_identifications)

    def test_06_action_view_task_single(self):
        bom_line_id = self._add_bom_line(self.service_in_project_hours)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        # view task action
        action = production_id.action_view_task()
        self.assertIn("form", action["view_mode"])
        self.assertIn("res_id", action)
        self.assertEqual(action["res_id"], production_id.task_ids.id)
        self.assertEqual(action["res_model"], "project.task")
        self.assertEqual(action["type"], "ir.actions.act_window")

    def test_07_action_view_task_multiple(self):
        bom_line_id1 = self._add_bom_line(self.service_in_project_hours)
        bom_line_id2 = self._add_bom_line(self.service_in_project_hours)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        # view task action
        action = production_id.action_view_task()
        self.assertIn("form", action["view_mode"])
        self.assertIn("res_id", action)
        self.assertEqual(action["res_id"], 0)
        self.assertEqual(action["res_model"], "project.task")
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertIn("domain", action)

    def test_08_cancel_production_order(self):
        bom_line_id = self._add_bom_line(self.service_in_project_hours)
        production_id = self._generate_mo(self.p1, self.bom, 3.0)
        production_id.project_id = self.project_id
        production_id.action_confirm()
        task_id = production_id.task_ids
        self.assertTrue(task_id)
        # store current chat/activity data for future uses
        previous_activity_ids = task_id.activity_ids
        previous_message_ids = task_id.message_ids
        # cancel production order
        production_id.action_cancel()
        # no warning message should be posted
        new_message_ids = task_id.message_ids - previous_message_ids
        self.assertEqual(len(new_message_ids), 0)
        # a new activity should be created
        new_activity_ids = task_id.activity_ids - previous_activity_ids
        self.assertEqual(len(new_activity_ids), 1)
        self.assertIn(
            "Exception(s) occurred on the production order(s)",
            new_activity_ids.note,
        )
