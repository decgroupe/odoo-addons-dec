# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

import time
import logging

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class ref_price(models.Model):
    """ Description """

    _name = 'ref.price'
    _description = 'Price'
    _order = 'date desc'

    reference_id = fields.Many2one(
        'ref.reference', 'Reference', ondelete='cascade', required=True
    )
    date = fields.Date('Date', required=True, default=fields.Datetime.now)
    value = fields.Float('Price')

    @api.multi
    def name_get(self):
        result = []
        for price in self:
            result.append((price.id, ''))

        return result
