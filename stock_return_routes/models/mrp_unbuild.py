# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Oct 2020

from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round


class MrpUnbuild(models.Model):
    _inherit = 'mrp.unbuild'

    def _generate_produce_moves(self):
        self.ensure_one()
        moves = super()._generate_produce_moves()
        edited_products = moves.mapped('product_id').\
            update_routes_after_return_to_stock()
        if edited_products:
            body = _('Following product\'s routes has been edited:<br><ul>')
            for product_names in edited_products.mapped('display_name'):
                body += '<li>%s</li>' % (product_names, )
            self.message_post(body=body)

        return moves

    def _generate_move_from_raw_moves(self, raw_move, factor):
        self.ensure_one()
        move = super()._generate_move_from_raw_moves(raw_move, factor)
        move.move_orig_ids = self.consume_line_ids
        return move
