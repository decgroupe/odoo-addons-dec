# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging
import werkzeug.routing
import werkzeug.utils

from functools import partial

import odoo
from odoo import api, models
from odoo import registry, SUPERUSER_ID
from odoo.http import request
from odoo.tools.safe_eval import safe_eval


logger = logging.getLogger(__name__)


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def binary_content(
        self,
        xmlid=None,
        model="ir.attachment",
        id=None,
        field="datas",
        unique=False,
        filename=None,
        filename_field="name",
        download=False,
        mimetype=None,
        default_mimetype="application/octet-stream",
        access_token=None,
    ):
        # allow fields from /odoo/addons/base/models/image_mixin.py
        if field in (
            "image",
            "image_1920",
            "image_1024",
            "image_512",
            "image_256",
            "image_128",
        ):
            if id and model in self.env:
                obj = self.env[model].browse(int(id))
                if field in obj._fields:
                    self = self.sudo()
        return super(Http, self).binary_content(
            xmlid=xmlid,
            model=model,
            id=id,
            field=field,
            unique=unique,
            filename=filename,
            filename_field=filename_field,
            download=download,
            mimetype=mimetype,
            default_mimetype=default_mimetype,
            access_token=access_token,
        )
