# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    public_code = fields.Char(
        string="Public Code",
        compute="_compute_public_code",
        inverse="_inverse_public_code",
        store=True,
        size=24,
        help="Commercial code used for public display, e.g. on e-commerce or POS.",
    )

    def _get_related_fields_variant_template(self):
        res = super()._get_related_fields_variant_template()
        res.append("public_code")
        return res

    @api.depends("product_variant_ids.public_code")
    def _compute_public_code(self):
        self._compute_template_field_from_variant_field("public_code")

    def _inverse_public_code(self):
        self._set_product_variant_field("public_code")

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        name, args = self.env["product.product"]._clear_args(name, args)
        # Make a search with default criteria
        result = super().name_search(
            name=name, args=args, operator=operator, limit=limit
        )
        result = self.env["product.product"]._append_extra_search(
            self._name, name, result, limit
        )
        return result
