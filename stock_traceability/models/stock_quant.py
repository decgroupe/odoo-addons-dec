# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020


from odoo import api, models, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _update_reserved_quantity(
        self,
        product_id,
        location_id,
        quantity,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False
    ):
        reserved_quants = []
        try:
            reserved_quants = super()._update_reserved_quantity(
                product_id, location_id, quantity, lot_id, package_id, owner_id,
                strict
            )
        except UserError as user_error:
            _logger.warning('%s (%f)', user_error.name, quantity)
            raise user_error
        return reserved_quants
