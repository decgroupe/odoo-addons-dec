# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestMrpScheduleCommon


class TestMrpSchedule(TestMrpScheduleCommon):
    """Tests for mrp_schedule module."""

    def test_01_schedule_date_fields(self):
        """Production records must expose schedule mapping expected by mixin."""
        production = self._new_production(state="draft")
        self._assert_schedule_fields(
            production,
            {
                "start": "date_planned_start",
                "stop": "date_planned_finished",
                "deadline": "date_planned_finished",
            },
        )

    def test_02_done_production_not_schedulable(self):
        """Done productions must not be considered schedulable."""
        production = self._new_production(state="done")
        self.assertFalse(production._is_schedulable())

    def test_03_cancelled_production_not_schedulable(self):
        """Cancelled productions must not be considered schedulable."""
        production = self._new_production(state="cancel")
        self.assertFalse(production._is_schedulable())

    def test_04_draft_production_is_schedulable(self):
        """Draft productions remain schedulable and compute field accordingly."""
        production = self._new_production(state="draft")
        production._compute_schedulable()
        self.assertTrue(production.schedulable)
