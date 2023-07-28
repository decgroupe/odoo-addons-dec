# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import http
from odoo.addons.report_aeroo.controllers.main import AerooReportController
from odoo.addons.web.controllers.main import serialize_exception
from odoo.addons.web_pdf_preview.controllers.main import set_content_disposition_inline


class PreviewAerooReportController(AerooReportController):
    @http.route("/web/report_aeroo", type="http", auth="user")
    @serialize_exception
    def generate_aeroo_report(
        self,
        report_id,
        record_ids,
        context,
        action_context,
        action_data,
        token,
        debug=False,
    ):
        result = super(PreviewAerooReportController, self).generate_aeroo_report(
            report_id,
            record_ids,
            context,
            action_context,
            action_data,
            token,
            debug=debug,
        )
        result = set_content_disposition_inline(result)
        return result

    @http.route("/report/preview_aeroo", type="http", auth="user")
    @serialize_exception
    def generate_aeroo_preview(
        self,
        report_id,
        record_ids,
        context,
        action_context,
        action_data,
        token,
        debug=False,
    ):
        return self.generate_aeroo_report(
            report_id,
            record_ids,
            context,
            action_context,
            action_data,
            token,
            debug=debug,
        )
