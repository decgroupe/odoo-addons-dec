# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2020

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_view_pricelist_items(self):
        action = self.env.ref(
            'product_pricelist_analysis.act_window_product_pricelist_item'
        ).read()[0]
        action['context'] = dict(self.env.context)
        action['context']['search_default_product_tmpl_id'] = self.id
        #action['context']['search_default_product_id'] = self.id
        return action
