# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2021

from odoo import api, fields, models

FAVORITE_SYMBOL = "📌"


class ProductTemplate(models.Model):
    _inherit = "product.template"

    favorite_ok = fields.Boolean(
        string="Is a favorite",
        default=False,
        readonly=True,
        help="Technical field automatically computed used to find a product "
        "already used on a sale, a purchase or on a BoM",
    )

    @api.model
    def autoset_ok(self):
        """Extend autoset_ok to also set favorite_ok on products used in BoMs."""
        # when autoset_ok is called, _set_attribute_ok is hooked to set
        # favorite_ok on already sold or purchased products
        res = super().autoset_ok()
        # in the same way, BoMs are browsed to compute `favorite_ok`
        self._autoset_favorite_ok()
        return res

    @api.model
    def _set_attribute_ok(self, ok_attribute, product_ids):
        """Extend attribute setter to also mark products as favorite."""
        res = super()._set_attribute_ok(ok_attribute, product_ids)
        if ok_attribute in ("sale_ok", "purchase_ok"):
            self._set_favorite_ok(product_ids)
        return res

    @api.model
    def _autoset_favorite_ok(self):
        """Search among all existing BoMs and set favorite_ok on component products."""
        product_ids = self.env["product.product"]
        # search among all existing BoM lines and collect component products
        for product_id, _count in self.env["mrp.bom.line"]._read_group(
            [], ["product_id"], ["__count"]
        ):
            if product_id:
                product_ids |= product_id
        self._set_favorite_ok(product_ids)

    @api.model
    def _set_favorite_ok(self, product_ids):
        """Mark given product_ids as favorite."""
        self._set_attribute_ok("favorite_ok", product_ids)

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Clean favorite symbol from name before searching and set name_search
        context."""
        # it is important to clean the name from symbols to avoid issues
        # with other modules that would alter the name_search behavior (typefast)
        names = super(ProductTemplate, self.with_context(name_search=True)).name_search(
            name=self._clean_favorite_symbol(name),
            args=args,
            operator=operator,
            limit=limit,
        )
        return names

    @api.depends("favorite_ok")
    def _compute_display_name(self):
        """Append 📌 symbol to display name for favorite products."""
        res = super()._compute_display_name()
        if self.env.context.get("name_search"):
            for record in self:
                if record.favorite_ok:
                    record.display_name = f"{record.display_name} {FAVORITE_SYMBOL}"
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
