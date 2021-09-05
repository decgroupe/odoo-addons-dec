# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Feb 2021

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self):
        res = super()._action_done()
        self.mapped('product_tmpl_id').update_default_sell_price()
        self.mapped('product_tmpl_id').update_default_purchase_price()
        return res
