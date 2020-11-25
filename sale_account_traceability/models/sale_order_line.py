# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, Aug 2020

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    invoice_lines = fields.Many2many(
        domain="[('invoice_type', '=', 'out_invoice'), ('product_id', '=', product_id),]"
    )
