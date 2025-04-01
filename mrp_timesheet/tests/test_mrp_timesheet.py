# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2025

from odoo.tests import Form

from odoo.addons.mrp_project_auto.tests.common import TestMrpProjectAutoCommon


class TestMrpTimesheet(TestMrpProjectAutoCommon):

    def setUp(self):
        super().setUp()
        self.production_user.action_create_employee()
        self.production_employee = self.production_user.employee_id

    def test_01_auto_project_from_orm(self):
        prod1_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/TEST_01A",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
            }
        )
        self.assertTrue(prod1_id)
        self.assertFalse(prod1_id.project_id)
        prod2_id = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/TEST_01B",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
                "allow_timesheets": True,
            }
        )
        self.assertTrue(prod2_id)
        self.assertTrue(prod2_id.project_id)

    def test_02_action_create_project(self):
        # WH/MO/00001
        production_id = self.env.ref("mrp.mrp_production_1")
        self.assertFalse(production_id.allow_timesheets)
        self.assertFalse(production_id.project_id)
        production_id.action_create_project()
        self.assertTrue(production_id.allow_timesheets)
        self.assertTrue(production_id.project_id)

    def test_03_auto_start_from_timesheets(self):
        # use _generate_mo to create a production order that will internally create
        # the needed stock moves according the existing bill of materials
        prod1_id = self._generate_mo(self.product1, self.product1_bom)
        prod1_id.action_create_project()
        prod1_id.planned_hours = 3
        self.assertEqual(prod1_id.planned_hours, 3)
        self.assertEqual(prod1_id.total_hours, 0)
        self.assertEqual(prod1_id.remaining_hours, 3)
        self.assertEqual(prod1_id.progress, 0)
        self.assertEqual(prod1_id.state, "draft")
        self.assertTrue(prod1_id.project_id)
        # create a first timesheet entry for this production
        al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        # even with a timesheet entry, the production order is still in draft state
        # because the timesheet entry is not confirmed yet
        self.assertEqual(prod1_id.total_hours, 1)
        self.assertEqual(prod1_id.remaining_hours, 2)
        self.assertAlmostEqual(prod1_id.progress, 33.33, places=2)
        self.assertEqual(prod1_id.state, "draft")
        # confirm the production order
        prod1_id.action_confirm()
        # also force all stock moves to be done to ensure compatibility with
        # `mrp_supply_progress`
        for move in prod1_id.move_raw_ids:
            move.state = "done"
        self.assertEqual(prod1_id.state, "confirmed")
        # create a second timesheet entry for this production
        al2 = self.env["account.analytic.line"].create(
            {
                "name": "Mounting drawer into desk",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        # the state is automatically updated to "In Progress" because the production
        # order is confirmed
        self.assertEqual(prod1_id.total_hours, 2)
        self.assertEqual(prod1_id.remaining_hours, 1)
        self.assertAlmostEqual(prod1_id.progress, 66.67, places=2)
        self.assertEqual(prod1_id.state, "progress")
        # create a third timesheet entry for this production
        al3 = self.env["account.analytic.line"].create(
            {
                "name": "Boxing for shipment",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 2,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        self.assertEqual(prod1_id.total_hours, 4)
        self.assertEqual(prod1_id.remaining_hours, -1)
        self.assertAlmostEqual(prod1_id.progress, 100, places=2)
        # state should remain "In Progress"
        self.assertEqual(prod1_id.state, "progress")

    def test_04_update_project(self):
        prod1_id = self._generate_mo(self.product1, self.product1_bom)
        prod1_id.action_create_project()
        prod1_project_id = prod1_id.project_id
        # create a first timesheet entry for this production
        al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        # create a second timesheet entry for this production
        al2 = self.env["account.analytic.line"].create(
            {
                "name": "Mounting drawer into desk",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        self.assertEqual(prod1_id.total_hours, 2)
        # manually change the project associated to the production order
        new_project_id = self.env["project.project"].create(
            {"name": "Another project for %s" % prod1_id.name}
        )
        prod1_id.project_id = new_project_id
        # ensure that the project_id of the timesheet entries is updated
        self.assertEqual(al1.project_id, new_project_id)
        self.assertEqual(al2.project_id, new_project_id)
        # now reassign the project_id to the original project but using an ignore key
        # that should avoid the automatic update of the project_id of the timesheet
        # entries
        prod1_id.with_context(ignore_constrains_project_timesheets=True).project_id = (
            prod1_project_id
        )
        # and check that timehseet entries are not updated
        self.assertEqual(al1.project_id, new_project_id)
        self.assertEqual(al2.project_id, new_project_id)

    def test_05_timesheet_entry_production_data(self):
        prod1_id = self._generate_mo(self.product1, self.product1_bom)
        prod1_id.action_create_project()
        # create a first timesheet entry for this production
        al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": prod1_id.project_id.id,
                "production_id": prod1_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        another_project_id = self.env["project.project"].create(
            {"name": "Another project"}
        )
        # create unrelated timesheet entries
        al2 = self.env["account.analytic.line"].create(
            {
                "name": "Contact our customer",
                "project_id": another_project_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        al3 = self.env["account.analytic.line"].create(
            {
                "name": "Preparing demonstration",
                "project_id": another_project_id.id,
                "employee_id": self.production_employee.id,
                "unit_amount": 1,  # one hour
                "date": prod1_id.date_planned_start,
            }
        )
        self.assertRegex(al1.production_identification, r"\[E-COM07\] Large Cabinet")
        self.assertFalse(al2.production_identification)
        # assign production order to the unrelated timesheet entry (using UI)
        al2_form = Form(al2, view="mrp_timesheet.hr_timesheet_line_form_view")
        al2_form.project_id = self.env["project.project"] # mandatory unset
        al2_form.production_id = prod1_id
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            prod1_id.project_id,
            "Timesheet entry should now have the same project as the production order",
        )
        # unassigning the production order should not change the project
        al2_form = Form(al2, view="mrp_timesheet.hr_timesheet_line_form_view")
        al2_form.production_id = self.env["mrp.production"]
        al2_form.save()
        self.assertEqual(
            al2.project_id,
            prod1_id.project_id,
            "Timesheet entry should have kept its project",
        )
        # assign production order to the second unrelated timesheet entry (using UI)
        # without clearing the project_id
        al3_form = Form(al3, view="mrp_timesheet.hr_timesheet_line_form_view")
        al3_form.production_id = prod1_id
        al3_form.save()
        self.assertEqual(
            al3.project_id,
            another_project_id,
            "Timesheet entry should have kept its project",
        )
