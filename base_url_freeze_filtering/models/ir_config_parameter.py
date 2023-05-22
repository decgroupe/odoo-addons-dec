# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import _, api, models
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)

WEB_BASE_URL_FREEZE = "web.base.url.freeze"


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    @ormcache()
    def _get_db_url_freeze_allowedlist(self):
        res = []
        allowedlist = config.get("db_url_freeze_allowedlist")
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def get_param(self, key, default=False):
        value = super().get_param(key, default=default)
        if (
            key == WEB_BASE_URL_FREEZE
            and value
            and self.env.cr.dbname not in self._get_db_url_freeze_allowedlist()
        ):
            _logger.info("%s forced to False", WEB_BASE_URL_FREEZE)
            value = False
        return value
