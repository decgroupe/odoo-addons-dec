# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import http
from odoo.addons.web.controllers.main import ReportController, serialize_exception
from odoo.addons.report_aeroo.controllers.main import AerooReportController


def set_content_disposition_inline(result):
    if 'Content-Disposition' in result.headers:
        result.headers['Content-Disposition'] = result.headers[
            'Content-Disposition'].replace('attachment', 'inline')
    return result

class PreviewReportController(ReportController):
    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        result = super(PreviewReportController,
                       self).report_download(data, token)
        result = set_content_disposition_inline(result)
        return result

    @http.route(['/report/preview'], type='http', auth="user")
    def report_preview(self, data, token):
        return self.report_download(data, token)


class PreviewAerooReportController(AerooReportController):
    @http.route('/web/report_aeroo', type='http', auth="user")
    @serialize_exception
    def generate_aeroo_report(self, action, token, debug=False):
        result = super(PreviewAerooReportController,
                       self).generate_aeroo_report(action, token, debug=debug)
        result = set_content_disposition_inline(result)
        return result

    @http.route('/report/preview_aeroo', type='http', auth="user")
    @serialize_exception
    def generate_aeroo_preview(self, action, token, debug=False):
        return self.generate_aeroo_report(action, token, debug=debug)
