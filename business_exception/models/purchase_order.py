# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _log_decrease_ordered_quantity(self, purchase_order_lines_quantities):
        """ Override `_log_decrease_ordered_quantity` from purchase_stock
            Internal use of the purchase_stock.exception_on_po template
        """
        _logger.debug('_log_decrease_ordered_quantity')
        super()._log_decrease_ordered_quantity(purchase_order_lines_quantities)

    def _activity_cancel_on_sale(self):
        """ Override `_activity_cancel_on_sale` from sale_purchase
            Internal use of the sale_purchase.exception_sale_on_purchase_cancellation
            template
        """
        _logger.debug('_activity_cancel_on_sale')
        super()._activity_cancel_on_sale(self)
