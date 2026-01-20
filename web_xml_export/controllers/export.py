# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

import json
import logging
import operator

from werkzeug.exceptions import InternalServerError

from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import osutil

from odoo.addons.web.controllers.export import Export, ExportFormat

from .xml_writer import ExportXmlWriter

_logger = logging.getLogger(__name__)


class ExportAddXMLSupport(Export):
    @http.route("/web/export/formats", type="json", auth="user", readonly=True)
    def formats(self):
        res = super().formats()
        res.append(
            {"tag": "xml", "label": "XML"},
        )
        return res


class XMLExport(ExportFormat, http.Controller):
    @http.route("/web/export/xml", type="http", auth="user")
    def web_export_xml(self, data):
        try:
            return self.process(data)
        except Exception as exc:
            _logger.exception("Exception during request handling.")
            payload = json.dumps(
                {
                    "code": 200,
                    "message": "Odoo Server Error",
                    "data": http.serialize_exception(exc),
                }
            )
            raise InternalServerError(payload) from exc

    @property
    def content_type(self):
        return "text/xml;charset=utf8"

    def filename(self, base):
        return super().filename(base)

    @property
    def extension(self):
        return ".xml"

    def process(self, data):
        params = json.loads(data)
        model, fields, ids, domain, import_compat = operator.itemgetter(
            "model", "fields", "ids", "domain", "import_compat"
        )(params)

        if not ids:
            Model = request.env[model].with_context(
                import_compat=import_compat, **params.get("context", {})
            )
            ids = Model.search(domain, offset=0, limit=False, order=False).ids

        with ExportXmlWriter(request.env) as xml_writer:
            response_data = xml_writer.generate_export_xml(
                model, fields, ids, import_compat
            )

        return request.make_response(
            response_data,
            headers=[
                (
                    "Content-Disposition",
                    content_disposition(
                        osutil.clean_filename(self.filename(model) + self.extension)
                    ),
                ),
                ("Content-Type", self.content_type),
            ],
        )
