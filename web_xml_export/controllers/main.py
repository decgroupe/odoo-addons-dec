# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

import json
import logging
import operator

from odoo import http
from odoo.http import content_disposition, request

from odoo.addons.web.controllers.main import Export, ExportFormat, serialize_exception


_logger = logging.getLogger(__name__)


class ExportAddXMLSupport(Export):
    @http.route("/web/export/formats", type="json", auth="user")
    def formats(self):
        res = super().formats()
        res.append(
            {"tag": "xml", "label": "XML"},
        )
        return res


class XMLExport(ExportFormat, http.Controller):
    @http.route("/web/export/xml", type="http", auth="user")
    @serialize_exception
    def index(self, data, token):
        return self.process(data, token)

    @property
    def content_type(self):
        return "text/xml;charset=utf8"

    def filename(self, base):
        return base + ".xml"

    def process(self, data, token):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = operator.itemgetter(
            "model", "fields", "ids", "domain", "import_compat"
        )(params)

        if not ids:
            Model = request.env[model].with_context(
                import_compat=import_compat, **params.get("context", {})
            )
            ids = Model.search(domain, offset=0, limit=False, order=False).ids

        response_data = request.env["xml.writer"].generate_export_xml(
            model, fields, ids, import_compat
        )

        return request.make_response(
            response_data,
            headers=[
                ("Content-Disposition", content_disposition(self.filename(model))),
                ("Content-Type", self.content_type),
            ],
            cookies={"fileToken": token},
        )
