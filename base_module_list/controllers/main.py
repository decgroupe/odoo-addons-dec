# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Aug 2023


import odoo
from odoo import SUPERUSER_ID, api, http
from odoo.modules.registry import Registry

URL_BASE_V1 = "/api/base_module_list/v1"

URL_MODULES = URL_BASE_V1 + "/Installed"


class BaseModuleListController(http.Controller):
    """Http Controller for base_module_list."""

    @http.route(URL_MODULES, type="json", methods=["POST"], auth="none", csrf=False)
    def get_installed_modules(self, **kwargs):
        """Return server-wide modules and installed modules for the given database."""
        res = {}
        res["*"] = odoo.conf.server_wide_modules
        dbname = kwargs.get("dbname")
        db_registry = Registry(dbname)
        with db_registry.cursor(readonly=True) as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            modules_ids = (
                env["ir.module.module"].sudo().search([("state", "=", "installed")])
            )
            res[env.cr.dbname] = sorted(modules_ids.mapped("name"))
        return res
