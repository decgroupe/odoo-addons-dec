# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from unittest.mock import patch

from odoo.addons.web_pdf_preview_aeroo.controllers.main import (
    AerooReportController,
    PreviewAerooReportController,
    set_content_disposition_inline,
)

from .common import TestWebPdfPreviewAerooCommon


class TestWebPdfPreviewAeroo(TestWebPdfPreviewAerooCommon):
    """Tests for web_pdf_preview_aeroo module."""

    def test_01_set_content_disposition_inline(self):
        """Ensure attachment responses are converted to inline previews."""
        response = self._make_response('attachment; filename="x.pdf"')
        set_content_disposition_inline(response)
        self.assertEqual(
            response.headers.get("Content-Disposition"),
            'inline; filename="x.pdf"',
        )

    def test_02_keep_response_without_disposition(self):
        """Ensure responses without Content-Disposition stay unchanged."""
        response = self._make_response(None)
        set_content_disposition_inline(response)
        self.assertFalse(response.headers.get("Content-Disposition"))

    def test_03_generate_preview_delegates_to_report(self):
        """Ensure controller enforces inline content disposition on reports."""
        controller = PreviewAerooReportController()
        with patch.object(
            AerooReportController,
            "generate_aeroo_report",
            return_value=self._make_response('attachment; filename="x.pdf"'),
        ) as generate_report:
            result = PreviewAerooReportController.generate_aeroo_report.__wrapped__(
                controller,
                report_id="1",
                record_ids="[]",
                context="{}",
                action_context="{}",
                action_data="{}",
                token="1",
                debug=False,
            )
        self.assertEqual(
            result.headers.get("Content-Disposition"),
            'inline; filename="x.pdf"',
        )
        generate_report.assert_called_once_with(
            "1",
            "[]",
            "{}",
            "{}",
            "{}",
            "1",
            debug=False,
        )
