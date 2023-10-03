# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def create(self, vals):
        product = super().create(vals)
        if vals.get("type") == "service":
            product.unset_route_ids()
        return product

    def write(self, vals):
        res = super().write(vals)
        if vals.get("type") == "service":
            self.unset_route_ids()
        return res

    def unset_route_ids(self):
        self.write({"route_ids": [(5, 0, 0)]})
