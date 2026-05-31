# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestAccountReportQwebCommon


class TestAccountReportQweb(TestAccountReportQwebCommon):
    """Tests for account_report_qweb module."""

    def test_01_report_template_labels(self):
        """Check that the invoice report uses the custom labels."""
        invoice = self._create_invoice()
        html = self._render_invoice_report_html(invoice)
        self.assertIn("Description", html)
        self.assertIn("Source Document", html)
        self.assertIn("Unit Price (Tax-Excluded)", html)
        self.assertIn("Disc.(%)", html)
        self.assertIn("Subtotal (Tax-Excluded)", html)
        self.assertIn("Total (Tax-Included)", html)
