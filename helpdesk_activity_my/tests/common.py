# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestHelpdeskActivityMyCommon(TransactionCase):
    """Common fixtures for helpdesk_activity_my tests."""

    @classmethod
    def setUpClass(cls):
        """Set up model and inherited views used by the tests."""
        super().setUpClass()
        cls.HelpdeskTicket = cls.env["helpdesk.ticket"]
        cls.ticket_tree_view = cls.env.ref("helpdesk_activity_my.ticket_tree_view")
        cls.ticket_kanban_view = cls.env.ref(
            "helpdesk_activity_my.helpdesk_ticket_kanban_view"
        )
