# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

from odoo.tests.common import TransactionCase


class TestWebCalendarOptions(TransactionCase):
    """Tests for web_calendar_options module."""

    def test_01_module_installed(self):
        """Verify the module is installed."""
        module = self.env["ir.module.module"].search(
            [
                ("name", "=", "web_calendar_options"),
                ("state", "in", ["to install", "installed"]),
            ],
            limit=1,
        )
        self.assertTrue(module, "web_calendar_options module should be installed")

    def test_02_depends_on_calendar(self):
        """Verify the module depends on both web and calendar."""
        module = self.env["ir.module.module"].search(
            [("name", "=", "web_calendar_options")], limit=1
        )
        dep_names = module.dependencies_id.mapped("name")
        self.assertIn("web", dep_names)
        self.assertIn("calendar", dep_names)
