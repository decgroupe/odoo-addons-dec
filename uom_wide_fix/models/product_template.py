# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.multi
    def action_fix_uom_consistency(self):
        for rec in self:
            self.env['stock.move'].search(
                ['product_tmpl_id', '=', rec.id],
                ['product_uom.category_id.id', '!=', rec.id],
            )
