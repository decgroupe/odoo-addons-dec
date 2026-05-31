# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import http

from odoo.addons.report_aeroo.controllers.main import AerooReportController


def set_content_disposition_inline(response):
    """Force inline content disposition for preview responses."""
    content_disposition = response.headers.get("Content-Disposition")
    if content_disposition:
        response.headers["Content-Disposition"] = content_disposition.replace(
            "attachment", "inline", 1
        )
    return response


class PreviewAerooReportController(AerooReportController):
    @http.route("/web/report_aeroo", type="http", auth="user")
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
        """Generate an Aeroo report and force inline content disposition."""
        result = super().generate_aeroo_report(
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
        """Generate the Aeroo preview through the standard report endpoint."""
        return self.generate_aeroo_report(
            report_id,
            record_ids,
            context,
            action_context,
            action_data,
            token,
            debug=debug,
        )
