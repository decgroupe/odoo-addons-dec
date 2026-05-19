# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from datetime import date, timedelta

from lxml import etree

from .common import TestCrmLeadActivityMyCommon


class TestCrmLeadActivityMy(TestCrmLeadActivityMyCommon):
    """Tests for crm_lead_activity_my module."""

    def test_01_list_view_fields(self):
        """Check that activity_my fields are present in the combined list view arch."""
        view_info = self.env["crm.lead"].get_view(view_type="list")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)

    def test_02_kanban_view_fields(self):
        """Check that activity_my fields are present in the combined kanban
        view arch."""
        view_info = self.env["crm.lead"].get_view(view_type="kanban")
        arch = etree.fromstring(view_info["arch"])
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)

    def test_03_crm_lead_has_mixin_fields(self):
        """Check that crm.lead has the fields from mail.activity.my.mixin."""
        self.assertIn("activity_my_ids", self.env["crm.lead"]._fields)
        self.assertIn("activity_my_state", self.env["crm.lead"]._fields)
        self.assertIn("activity_my_date_deadline", self.env["crm.lead"]._fields)

    def test_04_action_snooze(self):
        """Check that action_snooze postpones the next user activity by 7 days."""
        today = date.today()
        activity = self.lead.activity_schedule(
            activity_type_id=self.activity_type.id,
            date_deadline=today,
            user_id=self.env.uid,
        )
        self.assertEqual(activity.date_deadline, today)
        self.lead.action_snooze()
        expected = today + timedelta(days=7)
        self.assertEqual(activity.date_deadline, expected)
