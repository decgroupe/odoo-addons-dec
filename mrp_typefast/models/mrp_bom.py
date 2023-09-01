# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2023

from odoo import api, models


class MrpBom(models.Model):
    _name = "mrp.bom"
    _inherit = ["mrp.bom", "typefast.mixin"]
    _typefast_options = {
        "source": "name_get",
    }

    @api.depends("code")
    def _compute_typefast(self):
        super()._compute_typefast()
