# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestWebReportWorkflowCommon


class TestWebReportWorkflow(TestWebReportWorkflowCommon):
    """Tests for web_report_workflow module."""

    def test_01_external_layout_standard_contains_company_contact_block(self):
        """Check the customized company contact block is present."""
        arch = self._get_combined_arch(self.StandardLayoutView)
        company_headers = [
            node
            for node in arch.iter("div")
            if "company_header" in (node.get("class") or "")
        ]
        self.assertTrue(company_headers)
        self.assertEqual(company_headers[0].get("name"), "company_address")

    def test_02_external_layout_standard_contains_report_bank_footer(self):
        """Check footer keeps the report bank footer field placeholder."""
        arch = self._get_combined_arch(self.StandardLayoutView)
        t_fields = [node.get("t-field") for node in arch.iter() if node.get("t-field")]
        self.assertIn("company.report_bank_footer", t_fields)
