# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    manufacturable = fields.Boolean(
        compute="_compute_manufacturable",
        store=True,
    )

    @api.multi
    @api.depends('bom_ids', 'bom_ids.active', 'bom_ids.type')
    def _compute_manufacturable(self):
        product_ids = self.search(
            [('id', 'in', self.ids), ('bom_ids', '!=', False)]
        )
        for rec in product_ids:
            rec.manufacturable = rec.bom_ids.filtered('active') and \
                rec.bom_ids.filtered(lambda x: x.type == 'normal')
        for rec in self.filtered(lambda x: x.id not in product_ids.ids):
            rec.manufacturable = False
