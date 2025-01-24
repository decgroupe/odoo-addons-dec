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
        # create timehseet entry for this phonecall
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

        def search_for(text):
            res_ids = (
                self.analytic_line_model.with_user(self.user_admin)
                .with_context(**self._get_default_autofill_context())
                .name_search(text)
            )
            # extract id from the name get tuple (id, display_name) and browse data
            analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
            self.assertIn(self.al_id, analytic_line_ids)

        search_for("feedback")
        search_for("customer")
