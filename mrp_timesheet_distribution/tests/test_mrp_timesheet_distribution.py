# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from datetime import timedelta

from lxml import etree

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form

from odoo.addons.mrp_timesheet.tests.common import TestMrpTimesheetBase


class TestMrpTimesheetDistribution(TestMrpTimesheetBase):
    """Tests for mrp_timesheet_distribution module."""

    def setUp(self):
        """Set up shared test data."""
        super().setUp()
        self.wizard_model = self.env["mrp.distribute.timesheet"]
        # grant hr_timesheet access required to create analytic lines
        self.production_user.groups_id |= self.env.ref(
            "hr_timesheet.group_hr_timesheet_user"
        )
        # grant project manager access required to create tasks in any project
        self.production_user.groups_id |= self.env.ref("project.group_project_manager")
        # create two production orders; mrp_project_auto auto-attaches a project
        self.prod1 = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/DIST001",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
                "allow_timesheets": True,
            }
        )
        self.prod2 = self.production_model.with_user(self.production_user).create(
            {
                "name": "WH/MO/DIST002",
                "product_id": self.product1.id,
                "product_uom_id": self.product1.uom_id.id,
                "allow_timesheets": True,
            }
        )
        self.layout_reason = self.env.ref(
            "mrp_timesheet_distribution.layout_and_wiring"
        )
        self.other_reason = self.env.ref("mrp_timesheet_distribution.other")
        self.base_dt = fields.Datetime.from_string("2026-04-01 08:00:00")

    def _create_wizard(self, production_ids, unit_amount=2.0, **kwargs):
        """Create and return a distribution wizard record run as production_user."""
        vals = {
            "production_ids": [pid.id for pid in production_ids],
            "reason_id": self.layout_reason.id,
            "date_time": self.base_dt,
            "unit_amount": unit_amount,
        }
        vals.update(kwargs)
        return self.wizard_model.with_user(self.production_user).create(vals)

    def test_01_form_view_fields(self):
        """Check that expected fields are present in the form view arch."""
        view_info = self.env["mrp.distribute.timesheet"].get_view(view_type="form")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        expected = [
            "production_ids",
            "reason_id",
            "custom_reason",
            "date_time",
            "exclude_time",
            "excluded_start_time",
            "excluded_end_time",
            "unit_amount",
            "timesheet_line_ids",
        ]
        for field_name in expected:
            self.assertIn(field_name, field_names)

    def test_02_list_view_fields(self):
        """Check that expected fields are present in the line list view arch."""
        view_info = self.env["mrp.distribute.timesheet.line"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        expected = ["project_id", "production_id", "start_time", "end_time"]
        for field_name in expected:
            self.assertIn(field_name, field_names)

    def test_03_distribute_basic(self):
        """Distribute 2 hours over 2 production orders and check analytic lines."""
        wizard = self._create_wizard([self.prod1, self.prod2], unit_amount=2.0)
        self.assertEqual(len(wizard.timesheet_line_ids), 2)
        line1 = wizard.timesheet_line_ids[0]
        line2 = wizard.timesheet_line_ids[1]
        # each interval must be 1 hour (2h / 2 productions)
        diff1 = (line1.end_time - line1.start_time).total_seconds() / 3600
        diff2 = (line2.end_time - line2.start_time).total_seconds() / 3600
        self.assertAlmostEqual(diff1, 1.0, places=5)
        self.assertAlmostEqual(diff2, 1.0, places=5)
        # intervals must be contiguous
        self.assertEqual(line1.end_time, line2.start_time)
        analytic_count_before = self.env["account.analytic.line"].search_count([])
        wizard.action_distribute()
        analytic_count_after = self.env["account.analytic.line"].search_count([])
        self.assertEqual(analytic_count_after - analytic_count_before, 2)

    def test_04_distribute_with_exclusion(self):
        """Distribute time with a break excluded, splitting into 2 intervals."""
        # work period: 08:00 → 11:00 (3 h), break: 10:00 → 11:30 (straddles end)
        # interval 1: 08:00 → 10:00 (2 h split across 2 productions)
        # interval 2: 11:30 → 12:30 (1 h split across 2 productions)
        excluded_start = self.base_dt + timedelta(hours=2)
        excluded_end = self.base_dt + timedelta(hours=3, minutes=30)
        wizard = self._create_wizard(
            [self.prod1, self.prod2],
            unit_amount=3.0,
            exclude_time=True,
            excluded_start_time=excluded_start,
            excluded_end_time=excluded_end,
        )
        # 4 lines expected: 2 productions × 2 intervals
        self.assertEqual(len(wizard.timesheet_line_ids), 4)
        # total distributed time must still be 3h
        total_hours = sum(
            (ln.end_time - ln.start_time).total_seconds() / 3600
            for ln in wizard.timesheet_line_ids
        )
        self.assertAlmostEqual(total_hours, 3.0, places=5)
        analytic_count_before = self.env["account.analytic.line"].search_count([])
        wizard.action_distribute()
        analytic_count_after = self.env["account.analytic.line"].search_count([])
        self.assertEqual(analytic_count_after - analytic_count_before, 4)

    def test_05_distribute_no_lines_raises_error(self):
        """Raise ValidationError when unit_amount is zero and no lines are computed."""
        # unit_amount=0 → _compute_timesheet_line_ids produces no lines
        wizard = self._create_wizard([self.prod1, self.prod2], unit_amount=0.0)
        self.assertEqual(len(wizard.timesheet_line_ids), 0)
        with self.assertRaises(ValidationError):
            wizard.action_distribute()

    def test_06_custom_reason(self):
        """Distribute using a custom reason and verify the analytic line name."""
        wizard = self._create_wizard(
            [self.prod1],
            unit_amount=1.0,
            reason_id=self.other_reason.id,
            custom_reason="Special maintenance",
        )
        self.assertEqual(len(wizard.timesheet_line_ids), 1)
        analytic_count_before = self.env["account.analytic.line"].search_count([])
        wizard.action_distribute()
        analytic_count_after = self.env["account.analytic.line"].search_count([])
        self.assertEqual(analytic_count_after - analytic_count_before, 1)
        analytic_line = self.env["account.analytic.line"].search(
            [("production_id", "=", self.prod1.id)], limit=1
        )
        self.assertTrue(analytic_line)
        self.assertEqual(analytic_line.name, "Special maintenance")

    def test_07_form_view_modifiers(self):
        """custom_reason is invisible unless reason_id is 'other'."""
        wizard = self._create_wizard([self.prod1], unit_amount=1.0)
        view = "mrp_timesheet_distribution.mrp_distribute_timesheet_form_view"
        with Form(wizard, view=view) as form:
            # with layout_and_wiring reason, custom_reason should be invisible
            self.assertTrue(form._get_modifier("custom_reason", "invisible"))
            # switch to "other" reason → custom_reason becomes visible
            form.reason_id = self.other_reason
            self.assertFalse(form._get_modifier("custom_reason", "invisible"))
            # satisfy the required constraint before the form saves on exit
            form.custom_reason = "test reason"

    def test_08_excluded_times_modifier(self):
        """excluded_start/end_time are invisible when exclude_time is False."""
        # use unit_amount=0 so no lines exist (avoids Form onchange KeyError)
        wizard = self._create_wizard([self.prod1], unit_amount=0.0)
        view = "mrp_timesheet_distribution.mrp_distribute_timesheet_form_view"
        with Form(wizard, view=view) as form:
            form._perform_onchange("date_time")  # trigger computation of excluded times
            # `exclude_time` defaults to False, fields are invisible
            self.assertTrue(form._get_modifier("excluded_start_time", "invisible"))
            self.assertTrue(form._get_modifier("excluded_end_time", "invisible"))
            # enable exclusion, fields become visible
            form.exclude_time = True
            self.assertFalse(form._get_modifier("excluded_start_time", "invisible"))
            self.assertFalse(form._get_modifier("excluded_end_time", "invisible"))
