# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2026

from odoo import api, models


class UoM(models.Model):
    _inherit = "uom.uom"

    @api.constrains("category_id")
    def _validate_uom_category(self):
        if self.env.context.get("skip_uom_category_validation"):
            return
        return super()._validate_uom_category()

