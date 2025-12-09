# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model_create_multi
    def create(self, vals_list):
        product_ids = super().create(vals_list)
        for product_id in product_ids:
            if product_id.type == "service":
                product_id.unset_route_ids()
        return product_ids

    def write(self, vals):
        res = super().write(vals)
        if vals.get("type") == "service":
            self.unset_route_ids()
        return res

    def unset_route_ids(self):
        self.write({"route_ids": [(5, 0, 0)]})
