# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import Form, TransactionCase


class TestHrTimesheetAutofillCommon(TransactionCase):

    def _get_timesheet_form(self):
        """Enforce default view because two primary views with same sequence (1)
        exists for `account.analytic.line` model:
        - analytic.view_account_analytic_line_form
        - hr_timesheet.hr_timesheet_line_form
        """
        return Form(
            self.analytic_line_model,
            view="hr_timesheet.hr_timesheet_line_form",
        )

    def _get_default_autofill_context(self):
        # re-use autofill_* context defined in XML views
        ctx = {
            "autofill_search_order": "create_date desc",
            "autofill_name_search": True,
        }
        return ctx

    def _search_for(self, text, al_ids=False, exclude_ids=False):
        res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search(text)
        )
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        for al_id in al_ids:
            if exclude_ids and al_id in exclude_ids:
                self.assertNotIn(al_id, analytic_line_ids)
            else:
                self.assertIn(al_id, analytic_line_ids)
        return analytic_line_ids

    def setUp(self):
        super().setUp()
        self.analytic_line_model = self.env["account.analytic.line"]
        self.user_admin = self.env.ref("base.user_admin")
        self.user_marc = self.env.ref("base.user_demo")
        self.employee_admin = self.env.ref("hr.employee_admin")
        self.employee_marc = self.env.ref("hr.employee_qdp")
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
