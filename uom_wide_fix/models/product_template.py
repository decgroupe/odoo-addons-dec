# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_fix_uom_consistency(self):
        for rec in self:
            self.env["stock.move"].search(
                ["product_tmpl_id", "=", rec.id],
                ["product_uom.category_id.id", "!=", rec.id],
            )
