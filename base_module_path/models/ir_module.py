# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import _, api, fields, models, addons
from odoo.modules.module import get_module_path


class IrModule(models.Model):
    _inherit = "ir.module.module"

    addons_path = fields.Char(
        compute="_compute_path",
        store=True,
    )
    path = fields.Char(
        compute="_compute_path",
        store=True,
    )

    def _compute_path(self):
        self.path = ""
        self.addons_path = ""
        for rec in self:
            rec.path = get_module_path(rec.name)
            if rec.path:
                for adp in addons.__path__:
                    if rec.path.startswith(adp):
                        rec.addons_path = adp
                        # we assert that nested addons paths are not possible so we
                        # take the first match
                        break

    def action_recompute_path(self):
        self._compute_path()
