# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2023

import json

import odoo
from odoo import SUPERUSER_ID, api, http, registry

from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

URL_BASE_V1 = "/api/base_module_list/v1"

URL_MODULES = URL_BASE_V1 + "/Installed"


class BaseModuleListController(http.Controller):
    """Http Controller for Product Reference Application"""

    #######################################################################

    @http.route(URL_MODULES, type="json", methods=["POST"], auth="none", csrf=False)
    def get_installed_modules(self, **kwargs):
        res = {}
        res["*"] = odoo.conf.server_wide_modules
        context = {}
        dbname = request.jsonrequest.get("dbname")
        db_registry = registry(dbname)
        with api.Environment.manage(), db_registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, context)
            modules_ids = (
                env["ir.module.module"].sudo().search([("state", "=", "installed")])
            )
            res[env.cr.dbname] = sorted(modules_ids.mapped("name"))
        return res
