# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2025

from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon


class TestMrpTimesheetAutofill(TestHrTimesheetAutofillCommon):

    def setUp(self):
        super().setUp()
        # WH/MO/00001
        production_id = self.env.ref("mrp.mrp_production_1")
        # dedicated project for this production
        project_id = self.env["project.project"].create({"name": "MO/00001"})
        # brandon.freeman55@example.com
        partner_id = self.env.ref("base.res_partner_address_15")
        # filling the project with the partner and project
        production_id.write(
            {
                "project_id": project_id.id,
                "allow_timesheets": True,
                "partner_id": partner_id.id,
            }
        )
        # create timesheet entries for this production
        self.al1 = self.env["account.analytic.line"].create(
            {
                "name": "Picking products from stock",
                "project_id": project_id.id,
                "production_id": production_id.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": production_id.date_planned_start,
            }
        )
        self.al2 = self.env["account.analytic.line"].create(
            {
                "name": "Mounting drawer into desk",
                "project_id": project_id.id,
                "production_id": production_id.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": production_id.date_planned_start,
            }
        )
        self.al3 = self.env["account.analytic.line"].create(
            {
                "name": "Boxing for shipment",
                "project_id": project_id.id,
                "production_id": production_id.id,
                "employee_id": self.employee_admin.id,
                "unit_amount": 1,  # one hour
                "date": production_id.date_planned_start,
            }
        )
        self.al_ids = self.al1 | self.al2 | self.al3

    def test_01_search(self):
        # search by timesheet entry name
        self._search_for("picking", self.al1, self.al2 | self.al3)
        self._search_for("mounting", self.al2, self.al1 | self.al3)
        self._search_for("boxing", self.al3, self.al1 | self.al2)
        self._search_for("boxing", self.al3, self.al1 | self.al2)
        # search by production name
        self._search_for("WH/MO/00001", self.al_ids)
        # search by partner name
        self._search_for("brandon", self.al_ids)
        # search by product name
        self._search_for("FURN_7800", self.al_ids)
        self._search_for("desk", self.al_ids)
        self._search_for("[FURN_7800] Desk Combination", self.al_ids)

