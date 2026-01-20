# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2026


import json
import logging
from unittest.mock import patch

from odoo import http
from odoo.tests import common

from odoo.addons.web_xml_export.controllers.xml_writer import INDENT, ExportXmlWriter

_logger = logging.getLogger(__name__)


class TestWebXmlExportBase(common.HttpCase):
    """Base class for Web XML Export tests"""

    def setUp(self):
        super().setUp()
        self.session = self.authenticate("admin", "admin")
        self.result = False

    def _default_params(self, model):
        return {
            "domain": [],
            "fields": [
                {"name": field.name, "label": field.string}
                for field in model._fields.values()
            ],
            "groupby": [],
            "ids": False,
            "import_compat": False,
            "model": model._name,
        }

    def _mock_to_string(self, doc):
        self.result = doc.toprettyxml(indent=INDENT).encode("utf-8")
        return self.result

    def export(self, model, fields=None, params=None, timeout=60):
        if fields is None:
            fields = []
        if params is None:
            params = {}
        self.result = False

        if fields and "fields" not in params:
            params["fields"] = [
                {
                    "name": fname,
                    "label": "",
                    "type": "",
                }
                for fname in fields
            ]

        with patch.object(ExportXmlWriter, "to_string", self._mock_to_string):
            self.url_open(
                "/web/export/xml",
                data={
                    "data": json.dumps(dict(self._default_params(model), **params)),
                    "csrf_token": http.Request.csrf_token(self),
                },
                timeout=timeout,
            )
        return self.result

    def assertExportEqual(self, value, expected):
        """Asserts that the export value is "almost" equal to the expected value:
        - compare line by line
        - ignores differences in whitespace and encoding
        - generate a percentage of similarity if the values are different
        """
        if isinstance(value, bytes):
            value = value.decode("utf-8")
            _logger.debug(value)
        # Value Lines vs Expected Lines
        vLines = [line.strip() for line in value.strip().splitlines() if line.strip()]
        eLines = [
            line.strip() for line in expected.strip().splitlines() if line.strip()
        ]
        for i, (e_line, v_line) in enumerate(zip(eLines, vLines, strict=False)):
            self.assertEqual(
                e_line,
                v_line,
                msg=f"Difference at line {i + 1}",
            )
        self.assertEqual(
            len(eLines),
            len(vLines),
            msg=f"Number of lines differ: Expected {len(eLines)}, Got {len(vLines)}\n"
            + value,
        )
