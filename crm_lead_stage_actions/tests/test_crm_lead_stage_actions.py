# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2025

import datetime

from freezegun import freeze_time

from odoo.tests.common import TransactionCase


class TestCrmLeadStageActions(TransactionCase):

    def setUp(self):
        super().setUp()
        # tracks stages
        self.stage_new = self.env.ref("crm.stage_lead1")
        self.stage_qualified = self.env.ref("crm.stage_lead2")
        self.stage_proposition = self.env.ref("crm.stage_lead3")
        self.stage_won = self.env.ref("crm.stage_lead4")
        self.stage_lost = self.env.ref("crm_lead_stage_actions.stage_lead_lost")
        # get existing cases
        self.case_22 = self.env.ref("crm.crm_case_22")
        self.assertEqual(self.case_22.stage_id, self.stage_proposition)
        # already set to won in `odoo/addons/crm/data/crm_lead_demo.xml`
        self.case_23 = self.env.ref("crm.crm_case_23")
        self.assertEqual(self.case_23.stage_id, self.stage_won)
        # already set to lost in `odoo/addons/crm/data/crm_lead_demo.xml`
        self.case_28 = self.env.ref("crm.crm_case_28")
        self.assertFalse(self.case_28.active)
        self.assertEqual(self.case_28.stage_id, self.stage_new)
        # but default's module behaviour is too keep current state, so we manually
        # override it
        self.case_28.stage_id = self.stage_lost

    def _now(self):
        now = datetime.datetime.now().replace(microsecond=0)
        return now

    def test_01_action_set_lost(self):
        now = self._now()
        with freeze_time(now):
            self.assertFalse(self.case_22.date_closed)
            self.case_22.action_set_lost()
            self.assertEqual(self.case_22.stage_id, self.stage_lost)
            self.assertFalse(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)

    def test_02_action_set_won(self):
        now = self._now()
        with freeze_time(now):
            self.assertFalse(self.case_22.date_closed)
            self.case_22.action_set_won()
            self.assertEqual(self.case_22.stage_id, self.stage_won)
            self.assertTrue(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)

    def test_03_action_archive_keep_stage(self):
        self.assertEqual(self.case_22.stage_id, self.stage_proposition)
        self.case_22.action_archive()
        self.assertFalse(self.case_22.active)
        self.assertEqual(self.case_22.stage_id, self.stage_proposition)

    def test_04_action_set_won_from_archive(self):
        now = self._now()
        with freeze_time(now):
            self.case_22.action_archive()
            self.assertFalse(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now)

        now_p2s = now + datetime.timedelta(seconds=2)
        with freeze_time(now_p2s):
            self.case_22.action_set_won()
            self.assertEqual(self.case_22.stage_id, self.stage_won)
            self.assertTrue(self.case_22.active)
            self.assertEqual(self.case_22.date_closed, now_p2s)

    def test_05_set_stage(self):
        # drag-and-drop to columns in kanban view
        self.case_22.stage_id = self.stage_lost
        self.assertFalse(self.case_22.active)
        self.assertEqual(self.case_22.probability, 0.0)
        self.case_22.stage_id = self.stage_won
        self.assertTrue(self.case_22.active)
        self.assertEqual(self.case_22.probability, 100.0)
        self.case_22.stage_id = self.stage_proposition
        self.assertTrue(self.case_22.active)
        self.assertEqual(self.case_22.probability, self.stage_proposition.probability)
