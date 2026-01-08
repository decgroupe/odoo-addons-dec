# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2024

import logging

from odoo import models

logger = logging.getLogger(__name__)


class IrBinary(models.AbstractModel):
    _inherit = "ir.binary"

    def _find_record_check_access(self, record, access_token, field):
        if field in (
            # allow fields from /odoo/addons/base/models/image_mixin.py
            "image_1920",
            "image_1024",
            "image_512",
            "image_256",
            "image_128",
            # allow fields from /odoo/addons/base/models/avatar_mixin.py
            "avatar_1920",
            "avatar_1024",
            "avatar_512",
            "avatar_256",
            "avatar_128",
        ):
            return record.sudo()
        return super()._find_record_check_access(record, access_token, field)
