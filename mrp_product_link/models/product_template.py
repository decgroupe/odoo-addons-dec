# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, fields, api
from odoo.tools.float_utils import float_round


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_product_qty = fields.Float(
        'Manufactured', compute='_compute_mrp_product_qty'
    )

    @api.one
    def _compute_mrp_product_qty(self):
        super()._compute_mrp_product_qty()

    @api.multi
    def action_view_mos(self):
        action = super().action_view_mos()
        action['context'] = {
            'search_default_last_year_mo_order': 0,
        }
        return action