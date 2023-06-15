# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_product_qty = fields.Float(
        string="Manufactured",
        compute="_compute_mrp_product_qty",
    )

    def _compute_mrp_product_qty(self):
        super()._compute_mrp_product_qty()

    def action_view_mos(self):
        action = super().action_view_mos()
        action["context"] = {
            "search_default_last_year_mo_order": 0,
        }
        return action
