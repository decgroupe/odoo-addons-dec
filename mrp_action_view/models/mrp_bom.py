# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from odoo import api, models


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    def action_open_product(self):
        action = self.mapped("product_id").action_view()
        action["context"] = {}
        return action