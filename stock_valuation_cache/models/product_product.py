# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Feb 2021

import progressbar

from odoo import api, models, fields, _


class Product(models.Model):
    _inherit = "product.product"

    qty_available_cache = fields.Float('Quantity On Hand (Cache)', )

    @api.multi
    def _compute_qty_available_cache(self):
        for rec in self:
            rec.qty_available_cache = rec.qty_available
