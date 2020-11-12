# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Nov 2020

from odoo import api, models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    small_supply = fields.Boolean(
        string="Small Supply",
        help="If checked, then this product will be considered like a "
        "consumable stockable product",
    )

    is_consumable = fields.Boolean(compute='_compute_is_consumable')

    def _compute_is_consumable(self):
        for product in self:
            if product.type == 'consu':
                product.is_consumable = True
            elif product.type == 'product' and product.small_supply:
                product.is_consumable = True
