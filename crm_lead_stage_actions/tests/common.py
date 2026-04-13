# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

import datetime

from odoo.tests.common import TransactionCase


class TestCrmLeadStageActionsCommon(TransactionCase):
    """Base class with shared fixtures for crm_lead_stage_actions tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared stage references used by all test methods."""
        super().setUpClass()
        # tracks stages
        cls.stage_new = cls.env.ref("crm.stage_lead1")
        cls.stage_qualified = cls.env.ref("crm.stage_lead2")
        cls.stage_proposition = cls.env.ref("crm.stage_lead3")
        cls.stage_won = cls.env.ref("crm.stage_lead4")
        cls.stage_lost = cls.env.ref("crm_lead_stage_actions.stage_lead_lost")

    def setUp(self):
        """Set up per-test case references and initial state."""
        super().setUp()
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
        # but default's module behaviour is to keep current state, so we manually
        # override it
        self.case_28.stage_id = self.stage_lost

    def _now(self):
        """Return current datetime truncated to the nearest second."""
        now = datetime.datetime.now().replace(microsecond=0)
        return now
