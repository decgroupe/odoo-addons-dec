# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from odoo import fields

from .common import TestMailActivityScheduleCommon


class TestMailActivitySchedule(TestMailActivityScheduleCommon):
    """Tests for the mail_activity_schedule module."""

    def test_01_popup_form_view_fields(self):
        """Check planning fields are present in popup form view arch."""
        view_info = self.MailActivity.get_view(
            view_id=self.mail_activity_form_popup_view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_plannable", field_names)
        self.assertIn("date_start", field_names)
        self.assertIn("date_stop", field_names)

    def test_02_list_view_fields(self):
        """Check planning fields are present in list view arch."""
        view_info = self.MailActivity.get_view(
            view_id=self.mail_activity_tree_view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("date_start", field_names)
        self.assertIn("date_stop", field_names)

    def test_03_activity_type_form_field(self):
        """Check the plannable field is present in activity type form arch."""
        view_info = self.MailActivityType.get_view(
            view_id=self.mail_activity_type_form_view.id, view_type="form"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("plannable", field_names)

    def test_04_sync_activity_to_calendar_event(self):
        """Check date updates on activity are propagated to linked event."""
        activity, event = self._create_activity_with_event()
        new_start = "2026-05-31 09:15:00"
        new_stop = "2026-05-31 11:45:00"
        activity.write({"date_start": new_start, "date_stop": new_stop})
        event.invalidate_recordset()
        self.assertEqual(fields.Datetime.to_string(event.start), new_start)
        self.assertEqual(fields.Datetime.to_string(event.stop), new_stop)
