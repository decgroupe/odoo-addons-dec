# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa@decgroupe.com>, Sep 2021

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def action_show_details(self):
        action = super().action_show_details()
        # If show details is called from an MRP move, then there is no picking,
        # but we want see reserved lines so we override the default view to
        # force a full view instead of the suggested one:
        #   odoo/addons/stock/models/stock_move.py
        if not self.picking_id:
            view = self.env.ref('stock.view_stock_move_operations')
            action.update({
                'views': [(view.id, 'form')],
                'view_id': view.id,
            })
        return action
