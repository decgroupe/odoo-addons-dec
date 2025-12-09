# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        # Make a search with default criteria
        names = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        return self.product_tmpl_id.append_favorite_emoji(self._name, names)
