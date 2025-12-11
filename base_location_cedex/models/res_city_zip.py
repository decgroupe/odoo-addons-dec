# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2020

from odoo import _, fields, models


class ResCityZip(models.Model):
    _inherit = "res.city.zip"
    cedex = fields.Char()

    _sql_constraints = [
        (
            "name_city_uniq",
            "UNIQUE(name, cedex, city_id)",
            "You already have a zip with that code in the same city. "
            "The zip code must be unique within it's city",
        ),
    ]

    def format_name(self):
        self.ensure_one()
        custom_prefix = super().format_name()
        res = self.format_city_name_with_cedex(custom_prefix)
        return res

    def format_city_name_with_cedex(self, prefix=""):
        self.ensure_one()
        if not prefix:
            prefix = self.city_id.name
        city_name = prefix
        if self.cedex:
            if self.cedex.lower() in ("cedex", ".", "-", "_"):
                city_name = _(f"{city_name} Cedex")
            else:
                city_name = _(f"{city_name} Cedex {self.cedex}")
        return city_name
