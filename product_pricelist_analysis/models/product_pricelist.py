# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, May 2020

from odoo import models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def action_view_pricelist_items(self):
        action = self.env.ref(
            'product_pricelist_analysis.act_window_product_pricelist_item'
        ).read()[0]
        action['context'] = dict(self.env.context)
        action['context']['search_default_pricelist_id'] = self.id
        return action
