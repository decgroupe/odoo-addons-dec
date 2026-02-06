# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, fields, models


class Product(models.Model):
    _inherit = "product.product"

    public_code = fields.Char(
        string="Public Code",
        size=24,
        help="Commercial code used for public display, e.g. on e-commerce or POS. "
        "It is not used for internal purposes, and can be duplicated across variants.",
    )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        name, args = self._clear_args(name, args)
        # make a search with default criteria
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        result = self._append_extra_search(self._name, name, result, limit)
        return result

    def _clear_args(self, name, args):
        # if name starts with a wilcard, then clear arg domain, the purpose of this
        # is to allow searching on public code without being impacted by other criteria
        # like `sale_ok` or `purchase_ok` that are often used in combination with
        # product search
        if name and len(name) > 1 and name.startswith("*"):
            name = name[1:]
            args = None
        return name, args

    @api.model
    def _append_extra_search(self, model, name, name_search_result, limit=100):
        """Append search on specific fields to the result of `name_search`.
        The prupose of this method is to be inherited by other modules to add extra
        search criteria to the product search without having to reimplement the whole
        `name_search` method hook.
        """
        # FIXME: this implementation is not optimal as it always performs the extra
        # search even if not needed (out-of limit).
        if self.env.context.get("search_public_code"):
            result = self._append_public_code_search(
                model, name, name_search_result, limit
            )
        else:
            result = name_search_result
        return result

    @api.model
    def _append_public_code_search(self, model, name, name_search_result, limit=100):
        result = name_search_result
        if name:
            # make a specific search according to public code
            product_domain = [("public_code", "ilike", name + "%")]
            # check for state field to see if 'product_state_review' module
            # is installed or not
            if "state" in self.env[model]._fields:
                state_domain = ["|", ("state", "!=", "obsolete"), ("state", "=", False)]
                product_domain = state_domain + product_domain
            products = self.env[model].search(product_domain, limit=limit)
            for product in products:
                result.append(
                    (product.id, f"{product.display_name} ({product.public_code})")
                )
        return result
