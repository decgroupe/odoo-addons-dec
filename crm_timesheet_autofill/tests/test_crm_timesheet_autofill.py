# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon


class TestCrmTimesheetAutofill(TestHrTimesheetAutofillCommon):
    def setUp(self):
        super().setUp()
        # Office Design
        project_id = self.env.ref("project.project_project_1")
        # Office Design and Architecture
        self.case21 = self.env.ref("crm.crm_case_21")
        # Create some timesheet entries for this lead
        self.al1 = self.env["account.analytic.line"].create(
            {
                "name": "First contact with this lead",
                "project_id": project_id.id,
                "lead_id": self.case21.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": self.case21.create_date,
            }
        )
        self.al2 = self.env["account.analytic.line"].create(
            {
                "name": "Preparing quotation",
                "project_id": project_id.id,
                "lead_id": self.case21.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": self.case21.create_date,
            }
        )
        self.al_ids = self.al1 | self.al2

    def test_01_search(self):
        self._search_for("office", self.al_ids)
        self._search_for("contact", self.al_ids, self.al2)
        self._search_for("quotation", self.al_ids, self.al1)
