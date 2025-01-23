# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

from odoo.tests.common import Form
from odoo.addons.hr_timesheet_autofill.tests.common import TestHrTimesheetAutofillCommon

from unittest.mock import patch


class TestHrTimesheetAutofill(TestHrTimesheetAutofillCommon):

    def test_01_autofill(self):
        # enforce default view because two primary views with same sequence (1)
        # exists for `account.analytic.line` model:
        # - analytic.view_account_analytic_line_form
        # - hr_timesheet.hr_timesheet_line_form
        analytic_line_form = Form(
            self.analytic_line_model,
            view="hr_timesheet.hr_timesheet_line_form",
        )
        self.assertFalse(analytic_line_form.autofill_from_analytic_line_id)
        self.assertFalse(analytic_line_form.project_id)
        self.assertFalse(analytic_line_form.task_id)
        # get a previous entry ("On Site Visit" by "Tina Williamson"
        # on projet "Research & Development" task "Create new components")
        previous_line_id = self.env.ref("hr_timesheet.account_analytic_line_0")
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
        res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search("visit")
        )
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        self.assertIn(self.al_48, analytic_line_ids)
        self.assertIn(self.al_322, analytic_line_ids)

    def test_02_search_with_existing_args(self):
        domain = [("id", "=", self.al_48.id)]
        res_ids = (
            self.analytic_line_model.with_user(self.user_admin)
            .with_context(**self._get_default_autofill_context())
            .name_search("visit", args=domain)
        )
        # extract id from the name get tuple (id, display_name) and browse data
        analytic_line_ids = self.analytic_line_model.browse([x[0] for x in res_ids])
        self.assertIn(self.al_48, analytic_line_ids)
        self.assertNotIn(self.al_322, analytic_line_ids)

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
        self.assertIn(self.al_70, analytic_line_ids)
        self.assertIn(self.al_158, analytic_line_ids)
        self.assertIn(self.al_261, analytic_line_ids)
        for analytic_line_id in analytic_line_ids:
            self.assertEqual(analytic_line_id.amount, -200.0)
