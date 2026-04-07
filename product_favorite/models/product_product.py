# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, models

from .product_template import FAVORITE_SYMBOL


class Product(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Clean favorite symbol from name before searching and set name_search
        context."""
        # it is important to clean the name from symbols to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(Product, self.with_context(name_search=True)).name_search(
            name=self._clean_favorite_symbol(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    @api.depends("product_tmpl_id.favorite_ok")
    def _compute_display_name(self):
        """Append 📌 symbol to display name for favorite product variants."""
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            for product in self:
                if product.favorite_ok:
                    product.display_name = f"{product.display_name} {FAVORITE_SYMBOL}"
        return res

    def _search_display_name(self, operator, value):
        """Clean favorite symbol from search value before delegating to super."""
        if self.env.context.get("name_search"):
            # this steps is only a fallback in case of a direct call, the real cleaning
            # is done in name_search, but we want to be sure that the search is clean
            # in any case
            value = self._clean_favorite_symbol(value)
        res = super()._search_display_name(operator, value)
        return res

    def _clean_favorite_symbol(self, name):
        """Remove the favorite symbol suffix from a product name string."""
        # remove favorite symbol
        if name and name.endswith(FAVORITE_SYMBOL):
            name = name[: -len(FAVORITE_SYMBOL)].strip()
        return name
