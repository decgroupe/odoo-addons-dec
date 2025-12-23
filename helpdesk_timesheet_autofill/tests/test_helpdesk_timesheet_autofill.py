# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon


class TestHelpdeskTimesheetAutofill(TestHrTimesheetAutofillCommon):
    def setUp(self):
        super().setUp()
        # Office Design
        project_id = self.env.ref("project.project_project_1")
        # [HT00002] Damaged Products
        self.ticket2 = self.env.ref("helpdesk_mgmt.helpdesk_ticket_2")
        # Create some timesheet entries for this ticket
        self.al1 = self.env["account.analytic.line"].create(
            {
                "name": "First contact for this support",
                "project_id": project_id.id,
                "ticket_id": self.ticket2.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": self.ticket2.create_date,
            }
        )
        self.al2 = self.env["account.analytic.line"].create(
            {
                "name": "Preparing quotation",
                "project_id": project_id.id,
                "ticket_id": self.ticket2.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": self.ticket2.create_date,
            }
        )
        self.al_ids = self.al1 | self.al2

    def test_01_search(self):
        self._search_for("office", self.al_ids)
        self._search_for("contact", self.al_ids, self.al2)
        self._search_for("quotation", self.al_ids, self.al1)
