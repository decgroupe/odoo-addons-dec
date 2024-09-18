# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2024

import base64
import json

import werkzeug

from odoo import http
from odoo.addons.web.controllers.main import _serialize_exception
from odoo.http import request
from odoo.tools import html_escape

SHARING_URL = "/web/attachments/token"


class AttachmentSharingController(http.Controller):

    @http.route(SHARING_URL + "/<string:token>", type="http", auth="none")
    def get_shared_attachments(self, token, **kwargs):
        return_code = 200
        try:
            attachment_ids = (
                request.env["ir.attachment"]
                .sudo()
                .search([("sharing_token", "=", token)])
            )
            if attachment_ids:
                for attachment_obj in attachment_ids:
                    filecontent = base64.b64decode(attachment_obj.datas)
                    url_filename = werkzeug.urls.url_quote(attachment_obj.name)
                    disposition = f"attachment; filename={url_filename}"
                    return request.make_response(
                        filecontent,
                        [
                            ("Content-Type", attachment_obj.mimetype),
                            ("Content-Length", len(filecontent)),
                            ("Content-Disposition", disposition),
                        ],
                    )
            else:
                return_code = 404
                raise Exception("Attachment(s) not found")
        except Exception as e:
            se = _serialize_exception(e)
            error = {
                "code": return_code,
                "message": "Odoo Server Error",
                "data": se,
            }
            response = request.make_response(html_escape(json.dumps(error)))
            response.status_code = return_code
            return response
