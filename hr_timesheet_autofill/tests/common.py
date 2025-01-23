# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import TransactionCase


class TestHrTimesheetAutofillCommon(TransactionCase):

    def _get_default_autofill_context(self):
        # re-use autofill_* context defined in XML views
        ctx = {
            "autofill_search_order": "create_date desc",
            "autofill_name_search": True,
        }
        return ctx

    def setUp(self):
        super().setUp()
        self.analytic_line_model = self.env["account.analytic.line"]
        self.user_admin = self.env.ref("base.user_admin")
        self.user_marc = self.env.ref("base.user_demo")
        # 'Research & Development' / 'Document management' > 'On Site Visit'
        self.al_48 = self.env.ref("hr_timesheet.account_analytic_line_48")
        # 'Office Design' / 'Room 1: Decoration' > 'On Site Visit'
        self.al_322 = self.env.ref("hr_timesheet.account_analytic_line_322")

        ### Following lines have an amount = -200.00
        # 'Research & Development' / 'Planning and budget' > Delivery
        self.al_70 = self.env.ref("hr_timesheet.account_analytic_line_70")
        # 'Research & Development' / 'Useablity review' > Quality analysis
        self.al_158 = self.env.ref("hr_timesheet.account_analytic_line_158")
        # 'Office Design' / 'Office planning' > Quality analysis
        self.al_261 = self.env.ref("hr_timesheet.account_analytic_line_261")
