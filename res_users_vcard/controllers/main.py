# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

import pprint

from odoo import http, fields
from odoo.http import request
from odoo.tools.translate import _
import odoo.tools.convert as odoo_convert


class VCardController(http.Controller):
    """ Http Controller for VCard
    """

    #######################################################################

    @http.route('/vcard/<string:email>.vcf', type='http', auth="none")
    def test(self, email, **kwargs):
        employee = request.env['hr.employee'].sudo().search(
            [('work_email', '=', email)], limit=1
        )
        if employee:
            vcard = employee._generate_vcard()
            headers = [
                ('Content-Type', 'text/x-vcard; charset=iso-8859-1'),
                ('Content-Length', len(vcard)),
                (
                    'Content-Disposition',
                    'attachment; filename=' + email + '.vcf;'
                ),
                ('Cache-Control', 'no-cache'),
            ]
            return request.make_response(vcard, headers=headers)
        return ''
