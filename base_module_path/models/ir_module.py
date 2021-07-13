# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2021

from odoo import _, api, models, fields
from odoo.modules.module import get_module_path


class IrModule(models.Model):
    _inherit = "ir.module.module"

    path = fields.Char(compute="compute_path")

    @api.multi
    def compute_path(self):
        for rec in self:
            rec.path = get_module_path(rec.name)
