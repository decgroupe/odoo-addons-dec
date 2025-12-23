# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jul 2021

from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.depends("product_tmpl_id.default_code", "product_tmpl_id.name")
    def _compute_display_name(self):
        """Custom naming to quickly identify a Bill of Materials"""
        res = super()._compute_display_name()
        for rec in self:
            if rec.code:
                if rec.product_tmpl_id.default_code in rec.code:
                    name = f"[{rec.code}] {rec.product_tmpl_id.name}"
                else:
                    name = f"[{rec.code}] {rec.product_tmpl_id.display_name}"
                rec.display_name = name
        return res
