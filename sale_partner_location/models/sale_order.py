# -*- coding: utf-8 -*-
# Copyright (C) DEC SARL, Inc - All Rights Reserved.
# Written by Yann Papouin <y.papouin at dec-industrie.com>, May 2021

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_shipping_zip_id = fields.Many2one(
        'res.city.zip',
        related='partner_shipping_id.zip_id',
        string="Shipping Partner's ZIP",
        readonly=True,
        store=True,
    )
