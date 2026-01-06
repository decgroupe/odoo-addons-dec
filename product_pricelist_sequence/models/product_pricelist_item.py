# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"
    _order = "sequence, applied_on, min_quantity desc, categ_id desc, id desc"

    note = fields.Char(
        string="Rule Name",
        help="Explicit rule name for this pricelist line.",
    )
    # WARNING: do not set an handle widget for this field in XML views, the user must
    # be in control of the sequence value
    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Gives the order in which the pricelist items will be checked. "
        "The evaluation gives highest priority to lowest sequence.",
    )

    @api.depends("note")
    @api.depends("applied_on", "categ_id", "product_tmpl_id", "product_id")
    def _compute_name(self):
        res = super()._compute_name()
        for rec in self:
            if rec.note:
                rec.name = f"{rec.note} 🢒 {rec.name}"
        return res
