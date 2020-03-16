# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, Mar 2020

from odoo import http
from odoo.addons.web.controllers.main import ReportController, serialize_exception
from odoo.addons.report_aeroo.controllers.main import AerooReportController


class PreviewReportController(ReportController):
    @http.route(['/report/download'], type='http', auth="user")
    def report_download(self, data, token):
        result = super(PreviewReportController,
                       self).report_download(data, token)
        result.headers['Content-Disposition'] = result.headers[
            'Content-Disposition'].replace('attachment', 'inline')
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
        result.headers['Content-Disposition'] = result.headers[
            'Content-Disposition'].replace('attachment', 'inline')
        return result

    @http.route('/report/preview_aeroo', type='http', auth="user")
    @serialize_exception
    def generate_aeroo_preview(self, action, token, debug=False):
        return self.generate_aeroo_report(action, token, debug=debug)
