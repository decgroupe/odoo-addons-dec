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

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=5,
        help="Gives the order in which the pricelist items will be checked. "
        "The evaluation gives highest priority to lowest sequence.",
    )

    @api.depends(
        "categ_id",
        "product_tmpl_id",
        "product_id",
        "compute_price",
        "fixed_price",
        "pricelist_id",
        "percent_price",
        "price_discount",
        "price_surcharge",
        "note",
    )
    def _get_pricelist_item_name_price(self):
        super()._get_pricelist_item_name_price()
        for rec in self:
            if rec.note:
                rec.name = ("%s 🢒 %s") % (rec.note, rec.name)
