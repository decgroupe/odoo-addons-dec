# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestHrTimesheetAutofillCommon(TransactionCase):
    def _get_timesheet_form(self, context=None):
        """Enforce default view because two primary views with same sequence (1)
        exists for `account.analytic.line` model:
        - analytic.view_account_analytic_line_form
        - hr_timesheet.hr_timesheet_line_form
        """
        return Form(
            self.analytic_line_model.with_context(**context or {}),
            view="hr_timesheet.hr_timesheet_line_form",
        )

    def _get_default_autofill_context(self):
        # re-use autofill_* context defined in XML views
        ctx = {
            "autofill_search_order": "create_date desc",
            "autofill_name_search": True,
        }
        return ctx

    def _get_default_autofill_domain(self, env):
        # re-use default domain defined in XML views
        domain = [
            ("user_id", "=", env.user.id),
        ]
        return domain

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
        self.assertTrue(self.user_admin.exists())
        self.user_marc = self.env.ref("base.user_demo")
        self.assertTrue(self.user_marc.exists())
        self.employee_admin = self.env.ref("hr.employee_admin")
        self.assertTrue(self.employee_admin.exists())
        self.employee_marc = self.env.ref("hr.employee_qdp")
        self.assertTrue(self.employee_marc.exists())

        # 'Research & Development' / 'New portal system' > 'On Site Visit'
        # (Mitchel Admin)
        self.al_visit1 = self.env.ref(
            "hr_timesheet.project_2_task_7_account_analytic_line_5"
        )
        # 'Office Design' / 'Room 1: Decoration' > 'On Site Visit'
        # (Mitchel Admin)
        self.al_visit2 = self.env.ref(
            "hr_timesheet.project_1_task_6_account_analytic_line_22"
        )
        # 'Office Design' / 'Room 1: Decoration' > 'On Site Visit'
        # (Jennie Fletcher but no user)
        self.al_visit3 = self.env.ref(
            "hr_timesheet.project_1_task_6_account_analytic_line_9"
        )

        ### Following lines have an amount = -200.00
        # 'Research & Development' / 'Planning and budget' > 'Delivery'
        # (Mitchel Admin)
        self.al_delivery1 = self.env.ref(
            "hr_timesheet.project_2_task_3_account_analytic_line_12"
        )
        # 'Research & Development' / '' > 'Quality analysis'
        # (Mitchel Admin)
        self.al_qa1 = self.env.ref("hr_timesheet.working_hours_requirements")
        # 'Office Design' / 'Office planning' > 'Quality analysis'
        # (Mitchel Admin)
        self.al_qa2 = self.env.ref(
            "hr_timesheet.project_1_task_1_account_analytic_line_14"
        )
