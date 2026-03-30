# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

import time

from odoo.tests.common import TransactionCase, new_test_user


class TestCrmTimesheetPhonecallContext(TransactionCase):
    """Tests for crm_timesheet_phonecall_context module."""

    def setUp(self):
        """Set up test data."""
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.test_user = new_test_user(
            self.env,
            login="crm_timesheet_phonecall_context-user",
            context=ctx,
        )
        self.test_user.action_create_employee()
        self.employee = self.test_user.employee_id
        self.project_a = self.env["project.project"].create({"name": "Project A"})
        self.project_b = self.env["project.project"].create({"name": "Project B"})
        self.phonecall_a = self.env["crm.phonecall"].create(
            {
                "name": "Call for Project A",
                "project_id": self.project_a.id,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": self.test_user.id,
                "state": "open",
                "direction": "out",
            }
        )
        self.phonecall_b = self.env["crm.phonecall"].create(
            {
                "name": "Call for Project B",
                "project_id": self.project_b.id,
                "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "user_id": self.test_user.id,
                "state": "open",
                "direction": "out",
            }
        )

    def test_01_phonecall_domain_with_project(self):
        """phonecall_id_domain filters by project when project is set."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet line",
                "project_id": self.project_a.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        self.assertEqual(
            line.phonecall_id_domain,
            [("project_id", "=", self.project_a.id)],
        )

    def test_02_phonecall_domain_without_project(self):
        """phonecall_id_domain is empty when no project is set."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet line without project",
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        self.assertEqual(line.phonecall_id_domain, [])

    def test_03_phonecall_domain_changes_with_project(self):
        """phonecall_id_domain updates when project changes."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet line",
                "project_id": self.project_a.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        self.assertEqual(
            line.phonecall_id_domain,
            [("project_id", "=", self.project_a.id)],
        )
        line.project_id = self.project_b
        self.assertEqual(
            line.phonecall_id_domain,
            [("project_id", "=", self.project_b.id)],
        )

    def test_04_phonecall_domain_cleared_when_project_unset(self):
        """phonecall_id_domain becomes empty when project is removed."""
        line = self.env["account.analytic.line"].create(
            {
                "name": "Timesheet line",
                "project_id": self.project_a.id,
                "employee_id": self.employee.id,
                "unit_amount": 1,
            }
        )
        self.assertEqual(
            line.phonecall_id_domain,
            [("project_id", "=", self.project_a.id)],
        )
        line.project_id = False
        self.assertEqual(line.phonecall_id_domain, [])
