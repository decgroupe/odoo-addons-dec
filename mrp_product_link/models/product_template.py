# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_view_mos(self):
        action = super().action_view_mos()
        action["domain"] = [
            # ("state", "=", "done"),
            ('product_tmpl_id', 'in', self.ids)
        ]
        action["context"] = {
            "search_default_filter_plan_date": 0,
        }
        return action
