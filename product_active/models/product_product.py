# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        # When we toggle active state of a 'product.template', the new state
        # is propagated to variants ('product.product'). When adding
        # 'active_to_tmpl' to the write context, the active change will be
        # propagated the other side, from 'product.product' to
        # 'product.template' then 'product.template' to 'product.product'.
        if not self.env.context.get('active_to_tmpl_done'):
            if 'active' in vals and self.env.context.get('active_to_tmpl'):
                self.with_context(active_to_tmpl_done=True).\
                    product_tmpl_id.active = vals.get('active')
        return res
