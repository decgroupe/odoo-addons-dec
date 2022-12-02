# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _log_activity(self, render_method, documents):
        """ Override `_log_activity` from stock in order to replace responsible
            for specific documents
        """
        _logger.debug('_log_activity')
        filtered_documents = {}
        for (parent, responsible), rendering_context in documents.items():
            if parent._name == 'stock.picking':
                # Replace responsible with creator
                responsible = parent.create_uid
            filtered_documents[(parent, responsible)] = rendering_context
        super()._log_activity(render_method, filtered_documents)

    def _log_less_quantities_than_expected(self, moves):
        """ Override `_log_less_quantities_than_expected` from stock and
            sale_stock. Internal use of the sale_stock.exception_on_picking
            and stock.exception_on_picking templates
        """
        _logger.debug('_log_less_quantities_than_expected')
        super()._log_less_quantities_than_expected(moves)
