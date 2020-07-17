# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Override sale pricelist field from addons/sale/models/sale.py
    # Lock type to sale using domain attribute
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
        },
        domain=[('type', '=', 'sale')],
        help="Pricelist for current sales order."
    )
