# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from lxml import etree

from .common import TestHelpdeskActivityMyCommon


class TestHelpdeskActivityMy(TestHelpdeskActivityMyCommon):
    """Tests for helpdesk_activity_my module."""

    def test_01_list_view_fields(self):
        """Check activity_my fields are present in helpdesk list view arch."""
        view_info = self.HelpdeskTicket.get_view(
            view_id=self.ticket_tree_view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_date_deadline", field_names)

    def test_02_kanban_view_fields(self):
        """Check activity_my fields are present in helpdesk kanban view arch."""
        view_info = self.HelpdeskTicket.get_view(
            view_id=self.ticket_kanban_view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        field_names = [el.get("name") for el in arch.iter("field")]
        self.assertIn("activity_my_ids", field_names)
        self.assertIn("activity_my_state", field_names)

    def test_03_list_view_has_snooze_button(self):
        """Check the snooze button is present in helpdesk list view arch."""
        view_info = self.HelpdeskTicket.get_view(
            view_id=self.ticket_tree_view.id, view_type="list"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        snooze_buttons = arch.xpath("//button[@name='action_snooze_my']")
        self.assertEqual(len(snooze_buttons), 1)

    def test_04_kanban_view_has_snooze_action(self):
        """Check kanban template contains the snooze object action."""
        view_info = self.HelpdeskTicket.get_view(
            view_id=self.ticket_kanban_view.id, view_type="kanban"
        )
        arch = etree.fromstring(view_info["arch"].encode())
        snooze_actions = arch.xpath("//a[@name='action_snooze_my'][@type='object']")
        self.assertEqual(len(snooze_actions), 1)
