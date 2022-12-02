# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Nov 2020

import logging
from pprint import pformat

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class Product(models.Model):
    _inherit = 'product.product'

    def _convert_consu_to_small_supply(
        self,
        stock_location_ids=False,
        merge_quants=True,
        raise_exception=True
    ):
        res = {}.fromkeys(self.ids, {'before': {}, 'after': {}})
        for consu in self.filtered(lambda x: x.type == 'consu'):
            move_ids = self.env['stock.move']
            existing_move_lines = self.env['stock.move.line'].search(
                [
                    (
                        'product_id', 'in',
                        consu.mapped('product_variant_ids').ids
                    ),
                    ('state', 'in', ['partially_available', 'assigned']),
                ]
            )
            if existing_move_lines:
                move_ids = existing_move_lines.mapped('move_id')
                for move in move_ids:
                    res[consu.id]['before'][move.id] = move.state
                move_ids._do_unreserve()
            consu.small_supply = True
            consu.type = 'product'
            for location_id in stock_location_ids:
                qty_available = consu.with_context(
                    location=location_id.id
                ).legacy_qty_available
                available_qty, in_date = self.env[
                    'stock.quant']._update_available_quantity(
                        consu, location_id, qty_available
                    )
                print(
                    location_id.display_name, '=', qty_available, available_qty,
                    in_date
                )
            if move_ids:
                move_ids._action_assign()
                for move in move_ids:
                    res[consu.id]['after'][move.id] = move.state
        if merge_quants:
            self.env['stock.quant']._merge_quants()
            self.env['stock.quant']._unlink_zero_quants()
        #raise Exception('Testing only')
        for k, v in res.items():
            for move_id in v['before']:
                if v['before'][move_id] != v['after'][move_id]:
                    message = 'State is not consistent:' + pformat(res)
                    if raise_exception and not self.env.context.get(
                        'ignore_inconsistent_states'
                    ):
                        raise Exception(message)
                    else:
                        _logger.warning(message)

        return res

    def action_convert_consu_to_small_supply(self):
        stock_location_ids = self.env.ref('stock.stock_location_stock')
        self._convert_consu_to_small_supply(stock_location_ids)