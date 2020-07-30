# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jul 2020

from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round

class ProductTemplate(models.Model):
    _name = 'product.template'
    _inherit = 'product.template'

    in_quotation_product_qty = fields.Float(
        compute='_compute_in_quotation_product_qty',
        string='In Quotation',
    )

    @api.multi
    def _compute_in_quotation_product_qty(self):
        for template in self:
            template.in_quotation_product_qty = float_round(
                sum(
                    [
                        p.in_quotation_product_qty
                        for p in template.product_variant_ids
                    ]
                ),
                precision_rounding=template.uom_id.rounding
            )
