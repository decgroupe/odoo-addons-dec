# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from werkzeug.wrappers import Response

from odoo.tests.common import TransactionCase


class TestWebPdfPreviewAerooCommon(TransactionCase):
    """Common setup for web_pdf_preview_aeroo tests."""

    def _make_response(self, disposition):
        """Create a lightweight HTTP response with optional disposition."""
        headers = []
        if disposition:
            headers.append(("Content-Disposition", disposition))
        return Response("ok", headers=headers)
