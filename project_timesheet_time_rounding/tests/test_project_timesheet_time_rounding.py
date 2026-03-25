# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2026

from datetime import datetime

from freezegun import freeze_time

from odoo.tests import common


class TestTimesheetTimeRounding(common.TransactionCase):
    """Test the default value of date_time on `account.analytic.line` is rounded to
    the previous quarter of an hour."""

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()
        self.analytic_line_model = self.env["account.analytic.line"]

    @freeze_time("2026-03-25 14:00:00")
    def test_01_exact_boundary_hour(self):
        """Test that a time exactly on a full-hour boundary stays unchanged."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 0, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 0, 0))

    @freeze_time("2026-03-25 14:07:30")
    def test_02_floor_mid_period(self):
        """Test that a time mid-period is floored to the previous 15-min mark."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 0, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 0, 0))

    @freeze_time("2026-03-25 14:14:59")
    def test_03_floor_just_before_quarter(self):
        """Test that a time just before :15 is floored to :00."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 0, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 0, 0))

    @freeze_time("2026-03-25 14:15:00")
    def test_04_exact_quarter_boundary(self):
        """Test that a time exactly on :15 stays unchanged."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 15, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 15, 0))

    @freeze_time("2026-03-25 14:16:00")
    def test_05_floor_after_quarter_boundary(self):
        """Test that a time just after :15 is floored to :15."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 15, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 15, 0))

    @freeze_time("2026-03-25 14:29:59")
    def test_06_floor_just_before_half_hour(self):
        """Test that a time just before :30 is floored to :15."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 15, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 15, 0))

    @freeze_time("2026-03-25 14:30:00")
    def test_07_exact_half_hour_boundary(self):
        """Test that a time exactly on :30 stays unchanged."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 14, 30, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 14, 30, 0))

    @freeze_time("2026-03-25 23:59:59")
    def test_08_floor_end_of_day(self):
        """Test that a time near end-of-day is floored to :45 of the same hour."""
        result = self.analytic_line_model._default_date_time()
        self.assertEqual(result, datetime(2026, 3, 25, 23, 45, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 23, 45, 0))

    @freeze_time("2026-03-25 10:22:00")
    def test_09_default_get_applies_rounding(self):
        """Test that date_time default from default_get uses the rounding logic."""
        defaults = self.analytic_line_model.default_get(["date_time"])
        self.assertEqual(defaults.get("date_time"), datetime(2026, 3, 25, 10, 15, 0))
        # also validate the same logic through create
        line = self.analytic_line_model.create({"name": "Test Line"})
        self.assertEqual(line.date_time, datetime(2026, 3, 25, 10, 15, 0))
