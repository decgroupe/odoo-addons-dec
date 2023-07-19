# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import fields, models


class RefPrice(models.Model):
    _name = "ref.price"
    _description = "Price"
    _order = "date desc"

    reference_id = fields.Many2one(
        comodel_name="ref.reference",
        string="Reference",
        ondelete="cascade",
        required=True,
    )
    date = fields.Date(
        string="Date",
        required=True,
        default=lambda self: fields.Date.today(),
    )
    value = fields.Float("Price")
    product_count = fields.Integer("Products")

    def name_get(self):
        result = []
        for price in self:
            result.append((price.id, ""))

        return result
