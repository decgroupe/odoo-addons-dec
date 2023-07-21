# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models
from odoo.tools import ormcache
from odoo.tools.config import config, to_list


class WebEnvironmentRibbonBackend(models.AbstractModel):
    _inherit = "web.environment.ribbon.backend"

    @api.model
    @ormcache()
    def _get_db_ribbon_ignorelist(self):
        res = []
        ignorelist = config.get("db_ribbon_ignorelist")
        if ignorelist:
            res = to_list(ignorelist)
        return res

    @api.model
    def get_environment_ribbon(self):
        """
        This method returns the ribbon data from ir config parameters
        :return: dictionary
        """
        res = super().get_environment_ribbon()
        if self.env.cr.dbname in self._get_db_ribbon_ignorelist():
            res["name"] = ""
        return res
