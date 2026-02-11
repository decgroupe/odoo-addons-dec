# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo.tests.common import TransactionCase


class TestHelpdeskTimesheetCalendar(TransactionCase):
    """Tests for helpdesk_timesheet_calendar module."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
