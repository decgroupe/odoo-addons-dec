# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026


from odoo.addons.mrp_project_auto.tests.common import TestMrpProjectAutoCommon


class TestMrpTimesheetBase(TestMrpProjectAutoCommon):
    """Base class for testing MRP Timesheet module."""

    def setUp(self):
        super().setUp()
        self.production_user.action_create_employee()
        self.production_employee = self.production_user.employee_id
