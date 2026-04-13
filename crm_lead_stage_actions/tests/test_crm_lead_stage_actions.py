# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

import datetime

from freezegun import freeze_time

from .common import TestCrmLeadStageActionsCommon


class TestCrmLeadStageActions(TestCrmLeadStageActionsCommon):
    """Tests for crm_lead_stage_actions module."""

    def test_01_action_set_lost(self):
        """Setting a lead as lost moves it to the lost stage and sets date_closed."""
        now = self._now()
        with freeze_time(now):
            self.assertFalse(self.case_22.date_closed)
            self.case_22.action_set_lost()
            self.assertEqual(self.case_22.stage_id, self.stage_lost)
            self.assertTrue(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)

    def test_02_action_set_won(self):
        """Setting a lead as won moves it to the won stage and sets date_closed."""
        now = self._now()
        with freeze_time(now):
            self.assertFalse(self.case_22.date_closed)
            self.case_22.action_set_won()
            self.assertEqual(self.case_22.stage_id, self.stage_won)
            self.assertTrue(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)

    def test_03_action_archive_keep_stage(self):
        """Archiving a lead keeps its current stage unchanged."""
        self.assertEqual(self.case_22.stage_id, self.stage_proposition)
        self.case_22.action_archive()
        self.assertFalse(self.case_22.active)
        self.assertEqual(self.case_22.stage_id, self.stage_proposition)

    def test_04_action_set_won_from_archive(self):
        """Setting an archived lead as won updates date_closed without unarchiving."""
        now = self._now()
        with freeze_time(now):
            self.case_22.action_archive()
            self.assertFalse(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)
        now_p2s = now + datetime.timedelta(seconds=2)
        with freeze_time(now_p2s):
            self.case_22.action_set_won()
            self.assertEqual(self.case_22.stage_id, self.stage_won)
            self.assertFalse(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now_p2s)

    def test_05_set_stage(self):
        """Dragging a lead to another column in kanban triggers correct behaviour."""
        # drag-and-drop to columns in kanban view
        self.case_22.stage_id = self.stage_lost
        self.assertTrue(self.case_22.active)
        self.assertEqual(self.case_22.probability, 0.0)
        self.case_22.stage_id = self.stage_won
        self.assertTrue(self.case_22.active)
        self.assertEqual(self.case_22.probability, 100.0)
        self.case_22.stage_id = self.stage_proposition
        self.assertTrue(self.case_22.active)
        self.assertEqual(self.case_22.probability, self.stage_proposition.probability)
