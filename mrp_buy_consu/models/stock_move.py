# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Dec 2023

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _adjust_procure_method(self):
        """Exclude consumable move to buy"""
        excluded_moves = self.filtered(
            lambda x: x.bom_line_id
            and x.bom_line_id.buy_consumable
            and x.procure_method == "make_to_order"
        )
        return super(StockMove, self - excluded_moves)._adjust_procure_method()
