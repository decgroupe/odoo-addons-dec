# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

import logging
from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def create_line(
        self,
        product_id,
        product_uom_id,
        product_uom_qty=1.0,
        markup_percent=0
    ):
        self.ensure_one()
        vals = {
            'order_id': self.id,
            'product_id': product_id,
        }
        vals = self.env['sale.order.line'].play_onchanges(vals, ['product_id'])
        vals['product_uom'] = product_uom_id
        vals = self.env['sale.order.line'].play_onchanges(vals, ['product_uom'])
        vals['product_uom_qty'] = product_uom_qty
        vals = self.env['sale.order.line'].play_onchanges(
            vals, ['product_uom_qty']
        )
        if markup_percent:
            # We need to remove price_unit to get a new one, take a look on
            # _get_new_values
            # from oca/server-tools/onchange_helper/models/base.py
            vals.pop('price_unit')
            vals['markup_percent'] = markup_percent
            vals = self.env['sale.order.line'].play_onchanges(
                vals, ['markup_percent']
            )
        line = self.env['sale.order.line'].create(vals)
        return line.id
