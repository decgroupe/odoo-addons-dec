# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import logging
import werkzeug
import base64
import io
import functools

import odoo.http as http
from odoo.http import request
from odoo import _, tools
from odoo.tools.mimetypes import guess_mimetype
from odoo.modules import get_resource_path

_logger = logging.getLogger(__name__)

URL_BASE = "/web/static/signature"


class SignatureController(http.Controller):
    """ Http Controller for Signatures
    """

    #######################################################################

    # def _get_origins(self):
    #     return {
    #         'private': _("A private person"),
    #         'school': _("A school"),
    #         'company': _("A company "),
    #     }

    # def _get_company_label(self, origin):
    #     if origin == 'school':
    #         res = _('School')
    #     elif origin == 'company':
    #         res = _('Company')
    #     else:
    #         res = False
    #     return res

    # def _get_description(self):
    #     res = _("Company Name") + ':\n- \n'
    #     res += _("Full Address (street, zipcode, city)") + ':\n- \n'
    #     res += _("Your Request") + ':\n- \n'
    #     return res

    # def _save_attachments(self, model, id):
    #     for c_file in request.httprequest.files.getlist('attachment'):
    #         data = c_file.read()
    #         if c_file.filename:
    #             request.env['ir.attachment'].sudo().create(
    #                 {
    #                     'name': c_file.filename,
    #                     'datas': base64.b64encode(data),
    #                     'datas_fname': c_file.filename,
    #                     'res_model': model,
    #                     'res_id': id
    #                 }
    #             )

    # def _default_return(self):
    #     return werkzeug.utils.redirect("/contactus-thank-you")

    #######################################################################

    @http.route(
        URL_BASE + '/<string:signature_logo_filename>',
        type="http",
        auth="public",
    )
    def user_signature_logo(self, signature_logo_filename, **kw):
        domain = [
            ('active', '=', True),
            ('signature_logo_filename', '=', signature_logo_filename)
        ]
        user_id = request.env['res.users'].sudo().search(domain)
        if user_id and user_id.signature_logo:
            logo = user_id.signature_logo
            img_width = int(kw.get('w', 0))
            img_height = int(kw.get('h', 0))
            if img_width > 0 and img_height > 0:
                logo = tools.image_resize_image(
                    logo, size=(img_width, img_height), upper_limit=True
                )
            image_base64 = base64.b64decode(logo)
            image_data = io.BytesIO(image_base64)
            mimetype = guess_mimetype(image_base64, default='image/png')
            mtime = user_id.write_date
            response = http.send_file(
                image_data,
                filename=signature_logo_filename,
                mimetype=mimetype,
                mtime=mtime
            )
        else:
            placeholder = functools.partial(
                get_resource_path, 'web', 'static', 'src', 'img'
            )
            response = http.send_file(placeholder('placeholder.png'))

        return response
