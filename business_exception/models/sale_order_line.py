# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def _purchase_decrease_ordered_qty(self, new_qty, origin_values):
        """ Override `_purchase_decrease_ordered_qty` from sale_purchase
            Internal use of the exception_purchase_on_sale_quantity_decreased
            template
        """
        _logger.debug('_purchase_decrease_ordered_qty')
        super()._purchase_decrease_ordered_qty(new_qty, origin_values)
