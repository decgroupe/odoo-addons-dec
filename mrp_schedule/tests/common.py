# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestMrpScheduleCommon(TransactionCase):
    """Common fixtures and helpers for mrp_schedule tests."""

    def _new_production(self, state):
        """Build a non-persisted manufacturing order for state-based checks."""
        return self.env["mrp.production"].new({"state": state})

    def _assert_schedule_fields(self, record, expected_mapping):
        """Assert the schedule field mapping for a production record."""
        self.assertEqual(record._get_schedule_date_fields(), expected_mapping)
