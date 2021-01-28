# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Jan 2021

from odoo import models, api, _

import logging

_logger = logging.getLogger(__name__)


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def _log_downside_manufactured_quantity(self, moves_modification):
        """ Override `_log_downside_manufactured_quantity` from mrp
            Internal use of the mrp.exception_on_mo template
        """
        _logger.debug('_log_downside_manufactured_quantity')
        super()._log_downside_manufactured_quantity(moves_modification)

    def _log_manufacture_exception(self, documents, cancel=False):
        """ Override `_log_manufacture_exception` from base from mrp
            Internal use of the mrp.exception_on_mo template
        """
        _logger.debug('_log_manufacture_exception')
        super()._log_manufacture_exception(documents, cancel)
