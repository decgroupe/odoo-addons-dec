# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

import logging

from odoo import _, api, models
from odoo.tools import ormcache
from odoo.tools.config import config, to_list

_logger = logging.getLogger(__name__)

WEB_BASE_URL_FREEZE = "web.base.url.freeze"
DB_URL_FREEZE_ALLOWEDLIST = "db_url_freeze_allowedlist"

class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    @ormcache()
    def _get_db_url_freeze_allowedlist(self):
        """Only database with their names stored in the `DB_URL_FREEZE_ALLOWEDLIST` in
        the server config file are allowed to set the `web.base.url` param value when
        `WEB_BASE_URL_FREEZE` is `True`
        """
        res = []
        allowedlist = config.get(DB_URL_FREEZE_ALLOWEDLIST)
        if allowedlist:
            res = to_list(allowedlist)
        return res

    @api.model
    def get_param(self, key, default=False):
        """Check for any access to `WEB_BASE_URL_FREEZE` and override to `False` if the
        current database name in not in the allow list.
        """
        value = super().get_param(key, default=default)
        if (
            key == WEB_BASE_URL_FREEZE
            and value
            and self.env.cr.dbname not in self._get_db_url_freeze_allowedlist()
        ):
            _logger.info("%s forced to False", WEB_BASE_URL_FREEZE)
            value = False
        return value
