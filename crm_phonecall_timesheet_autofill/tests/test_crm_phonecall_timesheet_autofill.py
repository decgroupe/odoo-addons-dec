# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon


class TestCrmPhonecallTimesheetAutofill(TestHrTimesheetAutofillCommon):

    def setUp(self):
        super().setUp()
        # Client Feedback and Next Steps
        phonecall_id = self.env.ref("crm_phonecall_timesheet.call_5")
        # Office Design
        project_id = self.env.ref("project.project_project_1")
        # create timesheet entry for this phonecall
        self.al_id = self.env["account.analytic.line"].create(
            {
                "name": "Call with our customer",
                "project_id": project_id.id,
                "phonecall_id": phonecall_id.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": phonecall_id.date,
            }
        )

    def test_01_search(self):
        self._search_for("feedback", self.al_id)
        self._search_for("customer", self.al_id)
