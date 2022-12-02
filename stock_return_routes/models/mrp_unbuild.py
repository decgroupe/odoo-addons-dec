# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Oct 2020

from datetime import datetime

from odoo import models, _
from odoo.addons.tools_miscellaneous.tools.html_helper import (ul, div)


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    def _generate_produce_moves(self):
        self.ensure_one()
        moves = super()._generate_produce_moves()
        ids = moves.mapped('product_id').\
            update_routes_after_return_to_stock(self.name)
        edited_products = self.env['product.product'].browse(ids)
        if edited_products:
            title = _('Following product\'s routes has been edited:')
            product_lines = []
            for product_names in edited_products.mapped('display_name'):
                product_lines.append('<li>%s</li>' % (product_names, ))
            body = div(title) + ul(''.join(product_lines))
            self.message_post(body=body)

        return moves

    def _generate_move_from_raw_moves(self, raw_move, factor):
        self.ensure_one()
        move = super()._generate_move_from_raw_moves(raw_move, factor)
        move.move_orig_ids = self.consume_line_ids
        return move
