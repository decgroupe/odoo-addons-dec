# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from unittest.mock import patch

from odoo.osv import expression

from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon


class TestHrTimesheetAutofill(TestHrTimesheetAutofillCommon):
    def test_01_autofill(self):
        analytic_line_form = self._get_timesheet_form(
            context={"default_employee_id": self.employee_admin.id}
        )
        self.assertFalse(analytic_line_form.autofill_from_analytic_line_id)
        self.assertFalse(analytic_line_form.project_id)
        self.assertFalse(analytic_line_form.task_id)
        # get a previous entry ("On Site Visit" by "Tina Williamson"
        # on projet "Research & Development" task "Create new components")
        previous_line_id = self.env.ref(
            "hr_timesheet.project_2_task_6_account_analytic_line_1"
        )
        self.assertTrue(previous_line_id.project_id)
        self.assertTrue(previous_line_id.task_id)
        # set auto-fill
        analytic_line_form.autofill_from_analytic_line_id = previous_line_id
        self.assertTrue(analytic_line_form.project_id)
        self.assertTrue(analytic_line_form.task_id)
        self.assertEqual(analytic_line_form.project_id, previous_line_id.project_id)
        self.assertEqual(analytic_line_form.task_id, previous_line_id.task_id)
        # ensure auto-fill is not saved
        analytic_line_id = analytic_line_form.save()
        self.assertFalse(analytic_line_id.autofill_from_analytic_line_id)

    def test_02_search(self):
        model_with_context = self.analytic_line_model.with_user(
            self.user_admin
        ).with_context(**self._get_default_autofill_context())
        domain = self._get_default_autofill_domain(model_with_context.env)
        res_ids = model_with_context.name_search("visit", domain)
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        self.assertIn(self.al_visit1, analytic_line_ids)
        self.assertIn(self.al_visit2, analytic_line_ids)
        # this line is not added because not mapped to any user
        self.assertFalse(self.al_visit3.user_id)
        self.assertNotIn(self.al_visit3, analytic_line_ids)

    def test_02_search_with_existing_args(self):
        model_with_context = self.analytic_line_model.with_user(
            self.user_admin
        ).with_context(**self._get_default_autofill_context())
        domain = self._get_default_autofill_domain(model_with_context.env)
        domain = expression.AND([domain, [("id", "=", self.al_visit1.id)]])
        res_ids = model_with_context.name_search("visit", domain)
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        self.assertIn(self.al_visit1, analytic_line_ids)
        self.assertNotIn(self.al_visit2, analytic_line_ids)
        self.assertNotIn(self.al_visit3, analytic_line_ids)

    def test_02_search_too_short(self):
        """when search text is too short, only the default search based on name
        (description) will be processed
        """
        # search for an...alysis
        autofill_res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search("an")
        )
        for res in autofill_res_ids:
            self.assertIn("an", res[1].lower())
        # search for xy...lophone
        autofill_res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search("xy")
        )
        # no entries should have "do" in line name
        self.assertFalse(autofill_res_ids)
        # search for doc...ument
        autofill_res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search("doc")
        )
        # some entries should have "do" in project name
        for res in autofill_res_ids:
            self.assertIn("doc", res[1].lower())

    def test_03_search_hook_autofill_fields(self):
        # use different fields for autofill search
        def get_autofill_fields(_self):
            return [
                "name",
                "amount",
            ]

        with patch(
            "odoo.addons.hr_timesheet_autofill.models.account_analytic_line"
            ".AccountAnalyticLine.get_autofill_fields",
            new=get_autofill_fields,
        ):
            res_ids = (
                self.analytic_line_model.with_user(self.user_admin)
                .with_context(**self._get_default_autofill_context())
                .name_search("-200")
            )
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        self.assertIn(self.al_delivery1, analytic_line_ids)
        self.assertIn(self.al_qa1, analytic_line_ids)
        self.assertIn(self.al_qa2, analytic_line_ids)
        for analytic_line_id in analytic_line_ids:
            self.assertEqual(analytic_line_id.amount, -200.0)
