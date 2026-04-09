# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestProjectMarkdownCommon(TransactionCase):
    """Base class for project_markdown tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared test data."""
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "Test Project",
            }
        )
        cls.task = cls.env["project.task"].create(
            {
                "name": "Test Task",
                "project_id": cls.project.id,
            }
        )
