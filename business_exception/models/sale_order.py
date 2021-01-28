# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _log_decrease_ordered_quantity(self, documents, cancel=False):
        """ Override `_log_decrease_ordered_quantity` from sale_stock
            Internal use of the sale_stock.exception_on_so template
        """
        _logger.debug('_log_decrease_ordered_quantity')
        super()._log_decrease_ordered_quantity(documents, cancel)

    @api.multi
    def _activity_cancel_on_purchase(self):
        """ Override `_activity_cancel_on_purchase` from sale_purchase
            Internal use of the sale_stock.exception_purchase_on_sale_cancellation
            template
        """
        _logger.debug('_activity_cancel_on_purchase')
        super()._activity_cancel_on_purchase()
