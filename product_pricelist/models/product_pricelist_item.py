# Copyright (C) DEC SARL, Inc - All Rights Reserved.
#
# CONFIDENTIAL NOTICE: Unauthorized copying and/or use of this file,
# via any medium is strictly prohibited.
# All information contained herein is, and remains the property of
# DEC SARL and its suppliers, if any.
# The intellectual and technical concepts contained herein are
# proprietary to DEC SARL and its suppliers and may be covered by
# French Law and Foreign Patents, patents in process, and are
# protected by trade secret or copyright law.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from DEC SARL.
# Written by Yann Papouin <y.papouin@dec-industrie.com>, May 2020

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    _order = "sequence, applied_on, min_quantity desc, categ_id desc, id desc"

    note = fields.Char(
        'Rule Name',
        oldname='name',
        help="Explicit rule name for this pricelist line.",
    )

    sequence = fields.Integer(
        'Sequence',
        required=True,
        default=5,
        help=
        "Gives the order in which the pricelist items will be checked. \
The evaluation gives highest priority to lowest sequence."
    )

    @api.one
    @api.depends('categ_id', 'product_tmpl_id', 'product_id', 'compute_price', \
        'fixed_price', 'pricelist_id', 'percent_price', 'price_discount', \
        'price_surcharge', 'note')
    def _get_pricelist_item_name_price(self):
        super()._get_pricelist_item_name_price()
        if self.note:
            self.name = ('%s 🢒 %s') % (self.note, self.name)
