# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Mar 2020

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    summary = fields.Char(
        size=128,
        help="Order summary to quickly identify this order in treeview",
    )
