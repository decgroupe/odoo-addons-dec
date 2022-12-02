# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import _, api, models, fields
from odoo.modules.module import get_module_path


class IrModule(models.Model):
    _inherit = "ir.module.module"

    path = fields.Char(
        compute="_compute_path",
        store=True,
    )

    def _compute_path(self):
        for rec in self:
            rec.path = get_module_path(rec.name)

    def action_recompute_path(self):
        self._compute_path()
