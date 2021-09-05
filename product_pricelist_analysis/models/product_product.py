# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Sep 2020

from odoo import models


class Product(models.Model):
    _inherit = 'product.product'

    def action_view_pricelist_items(self):
        action = self.env.ref(
            'product_pricelist_analysis.act_window_product_pricelist_item'
        ).read()[0]
        action['context'] = dict(self.env.context)
        action['context']['search_default_product_tmpl_id'] = self.product_tmpl_id.id
        action['context']['search_default_product_id'] = self.id
        return action
