# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from .common import TestSaleReportQwebCommon


class TestSaleReportQweb(TestSaleReportQwebCommon):
    """Tests for sale_report_qweb module."""

    def test_01_report_template_labels(self):
        """Check that the sale order report uses the custom labels."""
        sale_order = self._create_sale_order()
        html = self._render_sale_report_html(sale_order)
        self.assertIn("Description", html)
        self.assertIn("Quantity", html)
        self.assertIn("Unit Price (Tax-Excluded)", html)
        self.assertIn("Taxes", html)
        self.assertIn("Subtotal (Tax-Excluded)", html)
        self.assertIn("Total (Tax-Included)", html)
