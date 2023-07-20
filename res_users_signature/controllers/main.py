# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2022

import base64
import functools
import io

import odoo.http as http
from odoo import _, tools
from odoo.http import request
from odoo.modules import get_resource_path
from odoo.tools.mimetypes import guess_mimetype


URL_BASE = "/web/static/signature"


class SignatureController(http.Controller):
    """Http Controller for Signatures"""

    @http.route(
        URL_BASE + "/<string:signature_logo_filename>",
        type="http",
        auth="public",
    )
    def user_signature_logo(self, signature_logo_filename, **kw):
        domain = [
            ("active", "=", True),
            ("signature_logo_filename", "=", signature_logo_filename),
        ]
        user_id = request.env["res.users"].sudo().search(domain)
        if user_id and user_id.signature_logo:
            logo = user_id.signature_logo
            img_width = int(kw.get("w", 0))
            img_height = int(kw.get("h", 0))
            if img_width > 0 and img_height > 0:
                logo = tools.image_resize_image(
                    logo, size=(img_width, img_height), upper_limit=True
                )
            image_base64 = base64.b64decode(logo)
            image_data = io.BytesIO(image_base64)
            mimetype = guess_mimetype(image_base64, default="image/png")
            mtime = user_id.write_date
            response = http.send_file(
                image_data,
                filename=signature_logo_filename,
                mimetype=mimetype,
                mtime=mtime,
            )
        else:
            placeholder = functools.partial(
                get_resource_path, "web", "static", "src", "img"
            )
            response = http.send_file(placeholder("placeholder.png"))

        return response
