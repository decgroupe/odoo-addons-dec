# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo.tests.common import TransactionCase


class TestProjectScheduleCommon(TransactionCase):
    """Common fixtures and helpers for project_schedule tests."""

    @classmethod
    def setUpClass(cls):
        """Create baseline project and task records."""
        super().setUpClass()
        cls.project_id = cls.env["project.project"].create(
            {
                "name": "Project Schedule Test",
            }
        )
        cls.task_id = cls.env["project.task"].create(
            {
                "name": "Project Schedule Task",
                "project_id": cls.project_id.id,
            }
        )

    def _assert_schedule_fields(self, record, expected_mapping):
        """Assert the schedule fields mapping for a given record."""
        self.assertEqual(record._get_schedule_date_fields(), expected_mapping)
