# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from lxml import etree

from odoo.tests.common import TransactionCase


class TestWebReportWorkflowCommon(TransactionCase):
    """Common setup and helpers for web_report_workflow tests."""

    @classmethod
    def setUpClass(cls):
        """Set up shared references to target QWeb views."""
        super().setUpClass()
        cls.StandardLayoutView = cls.env.ref("web.external_layout_standard")

    def _get_combined_arch(self, view):
        """Return the combined inherited arch for the given view."""
        return etree.fromstring(view.get_combined_arch().encode())
