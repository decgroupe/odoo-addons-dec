# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <ypa at decgroupe.com>, Mar 2020

from odoo import api, fields, models


class RefPrice(models.Model):
    """ Description """

    _name = 'ref.price'
    _description = 'Price'
    _order = 'date desc'

    reference_id = fields.Many2one(
        'ref.reference',
        'Reference',
        ondelete='cascade',
        required=True,
    )
    date = fields.Date(
        'Date',
        required=True,
        default=lambda self: fields.Date.today(),
    )
    value = fields.Float('Price')
    product_count = fields.Integer('Products')

    @api.multi
    def name_get(self):
        result = []
        for price in self:
            result.append((price.id, ''))

        return result
